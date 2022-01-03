import pandas as pd
import os
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

os.environ['MPLCONFIGDIR'] = '/tmp'

def rarityScoring(asset_data, slug):
    """
    Output: Rarity of each item.
    """
    asset_rarities = []

    for asset in asset_data['assets']:
        asset_rarity = 1

        for trait in asset['traits']:
            trait_rarity = trait['trait_count'] / 8888
            asset_rarity *= trait_rarity

        asset_rarities.append({
            'token_id': asset['token_id'],
            'name': f"{slug} {asset['token_id']}",
            'description': asset['description'],
            'rarity': asset_rarity,
            'traits': asset['traits'],
            'image_url': asset['image_url'],
            'collection': asset['collection']
        })

    #assets_sorted = sorted(asset_rarities, key=lambda asset: asset['rarity']) 
    return asset_rarities

def priceRarityGraph(asset_df, asset_rarities, slug):
    """
    Output: Price to rarity graph.
    """
    rarities = [asset['rarity'] for asset in asset_rarities]
    token_ids = [asset['token_id'] for asset in asset_rarities]
    

    queried_ids = asset_df["ID"]
    priced_apes = asset_df["Current Price"]

    all_apes_df = pd.DataFrame({"id": token_ids, "rarity": rarities})
    priced_aped_df = pd.DataFrame({"id": queried_ids, "price": priced_apes})

    result = pd.merge(priced_aped_df, all_apes_df, on="id")
    filtered_result = result[result['price'] < np.median(list(result['price']))]

    plt.figure(figsize=(16,12))
    sns.scatterplot(data=filtered_result, x='price', y='rarity')
    plt.title(f"Price to Rarity Scores of {slug}", fontsize = 16) #title
    plt.xlabel("Price", fontsize = 13) #x label
    plt.ylabel("Rarity", fontsize = 13) #y label
    plt.savefig("current_plot.jpg")
    plt.close()

    return