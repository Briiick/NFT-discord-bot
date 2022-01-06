import pandas as pd

def floorDepthCalc(floor, asset_df):
    """
    Output: The number (and value) of items currently listed at a price below 1.5x the current floor  (i.e. how many floor items traded it would take to raise the floor price by 50% and their total value in ETH).
    """
    floor15 = float(floor * 1.5)
    floor_depth = len(asset_df[asset_df['Current Price'] <= floor15].reset_index())
    return floor_depth

def passionIntensityCalc(floor, asset_df):
    """
    Output: The percentage of items currently listed for sale that would be priced at a gain if listed at the current floor price (i.e. the floor price of the collection is higher than the item’s last traded price). 
    """
    passionate_items = asset_df[asset_df['Previous Price'] < floor]
    passionate_items = passionate_items[passionate_items['Current Price'] >= floor]
    passionate_score = round(((len(passionate_items) / len(asset_df)) * 100), 4) 
    return passionate_score

def sentimentScoreCalc(floor, asset_df):
    """
    Output: The percentage of items currently listed for sale that are priced at a gain (i.e. the list price of an item is higher than its last traded price).
    """
    sentiment_items = asset_df[asset_df['Current Price'] > asset_df['Previous Price']]
    sentiment_items = sentiment_items[sentiment_items['Current Price'] >= floor]
    sentiment_score = round(((len(sentiment_items) / len(asset_df)) * 100), 4) 
    return sentiment_score