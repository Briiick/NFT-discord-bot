# import libraries
import pandas as pd
import os
import requests
import time
import random
from dotenv import load_dotenv
import time
import datetime

load_dotenv()

#upload opensea API key
my_key = os.getenv('opensea_api_key')
headers = {"X-API-KEY": my_key}

def parse_sale_data(sale_dict):
    """
    Parse out the important data from the sale dict which comes from the API

    Returns: Specific information collected about sales.
    
    Function from http://adilmoujahid.com/posts/2021/06/data-mining-meebits-nfts-python-opensea/
    """
    
    is_bundle = False

    # check sales
    if sale_dict['asset'] != None:
        id = sale_dict['asset']['token_id']
    elif sale_dict['asset_bundle'] != None:
        id = [asset['token_id'] for asset in sale_dict['asset_bundle']['assets']]
        is_bundle = True
    
    # assign addresses
    seller_address = sale_dict['seller']['address']
    buyer_address = sale_dict['winner_account']['address']
    
    # check for usernames
    try:
        seller_username = sale_dict['seller']['user']['username']
    except:
        seller_username = None    
    try:
        buyer_username = sale_dict['winner_account']['user']['username']
    except:
        buyer_username = None
    
    timestamp = sale_dict['transaction']['timestamp']
    total_price = float(sale_dict['total_price'])
    payment_token = sale_dict['payment_token']['symbol']
    usd_price = float(sale_dict['payment_token']['usd_price'])
    transaction_hash = sale_dict['transaction']['transaction_hash']
    
    # assign to dictionary
    result = {'is_bundle': is_bundle,
              'id': id,
              'seller_address': seller_address,
              'buyer_address': buyer_address,
              'buyer_username': buyer_username,
              'seller_username':seller_username,
              'timestamp': timestamp,
              'total_price': total_price, 
              'payment_token': payment_token,
              'usd_price': usd_price,
              'transaction_hash': transaction_hash}
    
    return result

def eventQuery(slug):
    """
    Query all successful sales transactions in the last 30 days.

    Args:
        slug (str): the slug of the collection for OpenSea
    """
    time_now = datetime.datetime.now()
    print(f"Current time: {time_now}")
    start_date = time_now - datetime.timedelta(30)
    print(f"Start date of query: {start_date}")
    # displaying unix timestamp after conversion
    start_date_unix = time.mktime(start_date.timetuple())
    print(f"Start date in unix: {start_date_unix}")
    offset = 0
    # df for storing results
    df_store = pd.DataFrame(columns=['is_bundle', 'id', 'seller_address', 'buyer_address',
                                     'buyer_username', 'seller_username', 'timestamp',
                                     'total_price', 'payment_token', 'usd_price', 'transaction_hash'])
    first = True
    next_page = 0
    while True:
        # dont use 'cursor' parameter if first run
        if first == True:
            params = {
                    'collection_slug': slug,
                    'only_opensea': True,
                    'event_type': 'successful',
                    'occurred_after': start_date_unix
            }
            first = False
        else:
            params = {
                    'collection_slug': slug,
                    'only_opensea': True,
                    'event_type': 'successful',
                    'occurred_after': start_date_unix,
                    'cursor': next_page
            }
        
        try:
            r = requests.get('https://api.opensea.io/api/v1/events',
                                    params=params,
                                    headers=headers)
            response_json = r.json()
        
        # if we get a throttled response, wait and try again
        except:
            print(r)
            print("Throttled. Trying again with more time.")
            time.sleep(10)
            r = requests.get('https://api.opensea.io/api/v1/events',
                                    params=params,
                                    headers=headers)
            response_json = r.json()
        
        # parse the response for key information
        next_page = response_json['next']
        sales = response_json['asset_events']
        parsed_sales = [parse_sale_data(sale) for sale in sales]
        # store into df_store
        temp_df = pd.DataFrame(parsed_sales)
        df_store = pd.concat([df_store, temp_df])
        
        # set break conditions
        print(f"Length of accessed data: {len(sales)}")
        if len(sales) < 20:
            break
        if offset > 2000:
            break
        # way of tracking iterations
        next_offset = offset + 20
        print(f"Scraping {slug} items {offset} to {next_offset}")
        
        offset += 20
        
        time.sleep(0.2)
        
    # primarily from http://adilmoujahid.com/posts/2021/06/data-mining-meebits-nfts-python-opensea/
    # parse out bundles
    df_store = df_store[(df_store['payment_token'] != 'USDC') & (df_store['is_bundle'] == False)].copy()
    # parse dates
    df_store['timestamp'] = pd.to_datetime(df_store['timestamp'])
    # converting sales price from WEI to ETH
    df_store['total_price'] = df_store['total_price']/10.**18
    # Calculating the sale prices in USD
    df_store['total_price_usd'] = df_store['total_price'] * df_store['usd_price']
    
    return df_store
    