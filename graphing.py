import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

os.environ['MPLCONFIGDIR'] = '/tmp'

def rarityScoring(asset_data, total_tokens, slug):
    """
    Input: The individual listed asset data.
    Output: Rarity of each item.
    """
    # list to store rarity scores by index
    asset_rarities = []
    
    # iterate through assets and calculate rarity
    for asset in asset_data['assets']:
        asset_rarity = 1
        
        # if the trait count is 0 we don't include
        for trait in asset['traits']:
            if trait['trait_count'] == 0:
                continue
            trait_rarity = 1 / (trait['trait_count'] / total_tokens)
            asset_rarity += trait_rarity

        # get rarities
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
    Input: Rarities of each item and each item price.
    Output: Price to rarity graph.
    """
    # process into lists
    rarities = [asset['rarity'] for asset in asset_rarities]
    token_ids = [asset['token_id'] for asset in asset_rarities]
    
    # get price data 
    queried_ids = asset_df["ID"]
    priced_apes = asset_df["Current Price"]

    # apes is just a idea of a collection we might be querying
    all_apes_df = pd.DataFrame({"id": token_ids, "rarity": rarities})
    priced_aped_df = pd.DataFrame({"id": queried_ids, "price": priced_apes})

    # take only ones listed by merging on id
    result = pd.merge(priced_aped_df, all_apes_df, on="id")
    # take only ones below median
    filtered_result = result[result['price'] < np.median(list(result['price']))]
    # finally, of those, take only ones above the floor
    nonfloor_filtered_result = filtered_result[filtered_result['price'] >= floor].reset_index(drop=True)
    #print(nonfloor_filtered_result)

    # plot
    # Initialize layout
    fig, ax = plt.subplots(figsize = (24, 16))

    # Add scatterplot
    ax.scatter(nonfloor_filtered_result['price'], 
               nonfloor_filtered_result['rarity'], 
               s=60, alpha=0.8, edgecolors="k")

    # Fit linear regression via least squares with numpy.polyfit
    # It returns an slope (b) and intercept (a)
    # deg=1 means linear fit (i.e. polynomial of degree 1)
    b, a = np.polyfit(list(nonfloor_filtered_result['price']), 
                      list(nonfloor_filtered_result['rarity']), 
                      deg=1)

    # Create sequence of 100 numbers from 0 to 100 
    xseq = np.linspace(floor, np.median(list(result['price'])), num=100)

    # Plot regression line
    ax.plot(xseq, a + b * xseq, color="k", lw=2.5);

    plt.suptitle(f"Price to Rarity Scores of {slug}", fontsize=30) #title
    ax.set(xlabel='Price', ylabel='Rarity Score')

    # label with id.
    def label_point(x, y, val, ax):
        a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
        for i, point in a.iterrows():
            ax.text(point['x']+.02, point['y'], str(point['val']))

    # call label function
    label_point(nonfloor_filtered_result["price"], nonfloor_filtered_result["rarity"], nonfloor_filtered_result["id"], plt.gca())  
    plt.tight_layout() # Add space at top
    plt.grid()
    plt.savefig("temp_plots/price_rarity_plot.png")
    plt.close()

    return