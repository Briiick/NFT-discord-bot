# import libraries
import pandas as pd
import os
import requests
import time
import random
from dotenv import load_dotenv

load_dotenv()

#upload opensea API key
my_key = os.getenv('opensea_api_key')
headers = {"X-API-KEY": my_key}


def collectionStatsQuery(slug):
    """
    Input: the slug of the collection for OpenSea
    Return: the holistic collection report for the projects scraped.
    """
    collection_data = []

    # get the collection data
    try:
        url = f"https://api.opensea.io/api/v1/collection/{slug}"
        
        r = requests.request("GET", url, headers=headers)
        output = list(r.json()["collection"]["stats"].values())
        discord_url = r.json()["collection"]["discord_url"]
        labelled_output = [slug] + output
        collection_data.append(labelled_output)

        cols = ['collection_name'] + list(r.json()["collection"]["stats"].keys())

    # if collection data doesn't show there's a problem!
    except:
        # store collection name and come back later
        print(f"JSON error for: {slug}")
        empty_df = pd.DataFrame()
        return empty_df

    # compile df of collection data and return
    collection_df = pd.DataFrame(collection_data, columns=cols)
    return collection_df, discord_url
