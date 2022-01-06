# import libraries
import pandas as pd
import os
import requests
import time
import numpy as np
from dotenv import load_dotenv

load_dotenv()

#upload opensea API key
my_key = os.getenv('opensea_api_key')
headers = {"X-API-KEY": my_key}


### Get asset data
def getOneAssetData(slug, total_supply):

    # iterate through and collect:
    ### item ids
    ### current price of those listed
    ### previous price of those listed
    ### image url
    offset = 0
    df_store = pd.DataFrame(columns=['ID', 'Current Price', 'Previous Price', 'URL'])
    asset_data = {'assets': []}
    while True:
        # we are only looking at the listed items
        # and need to flag the ones that have been listed before / store listed before prices

        params = {
            'collection': slug,
            'order_by': 'sale_count',
            'order_direction': 'asc',
            'offset': offset,
            'limit': 50
        }
        try:
            # query the assets
            r = requests.get('https://api.opensea.io/api/v1/assets',
                            params=params,
                            headers=headers)
            response_json = r.json()
          
        except KeyError:
            print(r)
            print("Throttled. Trying again with more time.")
            time.sleep(10)
            r = requests.get('https://api.opensea.io/api/v1/assets', params=params, headers=headers)
            response_json = r.json()

        # store asset data for rarity
        asset_data['assets'].extend(response_json['assets'])

        # for dataframe of values
        id_list = []
        price_list = []
        prev_price_list = []
        item_urls = []

        # ids
        for i in range(0, len(response_json['assets'])):

            # collect data
            if response_json['assets'][i]['sell_orders'] != None:

                token_id = response_json['assets'][i]['token_id']
                #print(token_id)
                current_price = float(
                    response_json['assets'][i]['sell_orders'][0]['current_price']) / 1000000000000000000
                if response_json['assets'][i]['last_sale'] != None:
                    prev_price = float(response_json['assets'][i]['last_sale']['total_price']) / 1000000000000000000
                else:
                    prev_price = 0
                item_url = response_json['assets'][i]['permalink']
                #print(item_url)
            else:
                continue

            # store it in lists
            id_list.append(token_id)
            price_list.append(current_price)
            prev_price_list.append(prev_price)
            item_urls.append(item_url)

        temp_df = pd.DataFrame({
            'ID': id_list,
            'Current Price': price_list,
            'Previous Price': prev_price_list,
            'URL': item_urls
        })

        # append lists to dataframe
        df_store = pd.concat([df_store, temp_df])

        next_offset = offset + 50
        # if the length of the json is less than 50, then break
        if len(response_json['assets']) < 50:
            break
        print(f"Scraping {slug} items {offset} to {next_offset}")

        offset += 50

        # or if end of road with api break
        if offset == 10050:
            break

        # if you want to add a delay in case you get throttled
        time.sleep(0.2)

    ### ADD IN BIT FOR GOING OVER 10000
    if total_supply > 10000:
        # generate list of lists with 30 items in each
        # that make it to num_items
        # generate list
        rest_of_items = np.arange(10000, total_supply)
        # keep checking length
        while rest_of_items.any():
            n = 30
            if len(rest_of_items) < 30:
                n = len(rest_of_items)
            templist = rest_of_items
            templist, rest_of_items = templist[:n], rest_of_items[n:]
            int_list = [int(i) for i in templist]
            first = int_list[0]
            last = int_list[-1]
            print(f"Scraping {slug} items {first} to {last}")
            # now that we have a list of values
            # we can use the opensea api
            params = {
                'collection': slug,
                'order_by': 'pk',
                'order_direction': 'asc',
                'token_ids': int_list,
                'limit': 50
            }

            # query the assets
            try:
                r = requests.get('https://api.opensea.io/api/v1/assets', params=params, headers=headers)
                response_json = r.json()

            except KeyError:
                # try again with more time if throttled
                print(r)
                print("Throttled. Trying again with more time.")
                time.sleep(10)
                r = requests.get('https://api.opensea.io/api/v1/assets', params=params, headers=headers)
                response_json = r.json()

            # for rarity data
            asset_data['assets'].extend(response_json['assets'])

            # ids
            for i in range(0, len(response_json['assets'])):

                # collect data
                if response_json['assets'][i]['sell_orders'] != None:

                    token_id = response_json['assets'][i]['token_id']
                    #print(token_id)
                    current_price = float(
                        response_json['assets'][i]['sell_orders'][0]['current_price']) / 1000000000000000000
                    if response_json['assets'][i]['last_sale'] != None:
                        prev_price = float(response_json['assets'][i]['last_sale']['total_price']) / 1000000000000000000
                    else:
                        prev_price = 0
                    item_url = response_json['assets'][i]['permalink']
                    #print(item_url)
                else:
                    continue

                # store it in lists
                id_list.append(token_id)
                price_list.append(current_price)
                prev_price_list.append(prev_price)
                item_urls.append(item_url)

            temp_df = pd.DataFrame({
                'ID': id_list,
                'Current Price': price_list,
                'Previous Price': prev_price_list,
                'URL': item_urls
            })

            # append lists to dataframe
            df_store = pd.concat([df_store, temp_df])

            time.sleep(0.2)

    return df_store, asset_data
