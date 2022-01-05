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
    Returns the holistic collection report for the projects scraped.
    """
    collection_data = []

    try:
        url = f"https://api.opensea.io/api/v1/collection/{slug}/stats"

        r = requests.get(url, headers=headers)

        output = list(r.json()["stats"].values())
        labelled_output = [slug] + output
        collection_data.append(labelled_output)

        cols = ['collection_name'] + list(r.json()["stats"].keys())

    except:
        # store collection name and come back later
        print(f"JSON error for: {slug}")
        empty_df = pd.DataFrame()
        return empty_df

    collection_df = pd.DataFrame(collection_data, columns=cols)
    # store as pickle
    collection_df.to_pickle("data/collection_stats.pkl")
    return collection_df
