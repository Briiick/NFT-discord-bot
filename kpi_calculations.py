import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def floorDepthCalc(floor, asset_df):
    """
    Input: The floor price of the collection and the asset information.
    Output: The number (and value) of items currently listed at a price below X and the current floor  (i.e. how many floor items traded it would take to raise the floor price by Y% and their total value in ETH).
    """
    floor2 = float(floor * 1.2)
    floor4 = float(floor * 1.4)
    floor6 = float(floor * 1.6)
    floor8 = float(floor * 1.8)
    floor10 = float(floor * 2)
    floor_val_arr = [floor2, floor4, floor6, floor8, floor10]
    floor_depth = len(asset_df[asset_df['Current Price'] == floor].reset_index())
    floor_depth2 = len(asset_df[asset_df['Current Price'] <= floor2].reset_index())
    floor_depth4 = len(asset_df[asset_df['Current Price'] <= floor4].reset_index())
    floor_depth6 = len(asset_df[asset_df['Current Price'] <= floor6].reset_index())
    floor_depth8 = len(asset_df[asset_df['Current Price'] <= floor8].reset_index())
    floor_depth10 = len(asset_df[asset_df['Current Price'] <= floor10].reset_index())
    floor_depth_arr = [floor_depth, floor_depth2, floor_depth4, floor_depth6, floor_depth8, floor_depth10]
    return floor_val_arr, floor_depth_arr

def inTheMoney(floor, asset_df):
    """
    Output: The percentage of items currently listed for sale that would be priced at a gain if listed at the current floor price (i.e. the floor price of the collection is higher than the item’s last traded price). 
    """
    passionate_items = asset_df[asset_df['Previous Price'] < floor]
    passionate_items = passionate_items[passionate_items['Current Price'] >= floor]
    passionate_score = round(((len(passionate_items) / len(asset_df)) * 100), 2) 
    return passionate_score

def pricedAtGain(floor, asset_df):
    """
    Output: The percentage of items currently listed for sale that are priced at a gain (i.e. the list price of an item is higher than its last traded price).
    """
    sentiment_items = asset_df[asset_df['Current Price'] > asset_df['Previous Price']]
    sentiment_items = sentiment_items[sentiment_items['Current Price'] >= floor]
    sentiment_score = round(((len(sentiment_items) / len(asset_df)) * 100), 2) 
    return sentiment_score

def buyersellerCalc(df, buyer):
    if buyer == True:
        query_string = 'buyer_address'
    else:
        query_string = 'seller_address'
    storage = []
    for address in df[query_string].value_counts().index[:10]:
        data = {}
        data[query_string] = address
        if buyer == True:
            data['buyer_username'] = df[df[query_string] == address]['buyer_username'].iloc[0]
            data['number_buys'] = len(df[df[query_string] == address])
        else:
            data['seller_username'] = df[df[query_string] == address]['seller_username'].iloc[0]
            data['number_sales'] = len(df[df[query_string] == address])
        data['min_price'] = df[df[query_string] == address]['total_price'].min()
        data['max_price'] = df[df[query_string] == address]['total_price'].max()
        data['mean_price'] = df[df[query_string] == address]['total_price'].mean()
        storage.append(data)
    
    return pd.DataFrame(storage)
    