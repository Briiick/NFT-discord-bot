import pandas as pd
import os
import numpy as np
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
            
            trait_rarity = 1 / (trait['trait_count'] / len(asset_data['assets']))
            asset_rarity += trait_rarity

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

def priceRarityGraph(asset_df, asset_rarities, slug, floor):
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
    nonfloor_filtered_result = filtered_result[filtered_result['price'] >= floor]

    # plot
    fig = plt.figure(figsize=(24,16))
    ax = fig.add_subplot(111)
    ax = sns.lmplot(data=nonfloor_filtered_result,
                    x='price',
                    y='rarity',
                    fit_reg=True,
                    height= 8,
                    aspect= 2 )

    plt.suptitle(f"Price to Rarity Scores of {slug}", fontsize=18) #title
    ax.set(xlabel='Price', ylabel='Rarity Score')

    def label_point(x, y, val, ax):
        a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
        for i, point in a.iterrows():
            ax.text(point['x']+.02, point['y'], str(point['val']))

    label_point(nonfloor_filtered_result["price"], nonfloor_filtered_result["rarity"], nonfloor_filtered_result["id"], plt.gca())  
    plt.tight_layout() # Add space at top
    plt.savefig("price_rarity_plot.png")
    plt.close()

    return