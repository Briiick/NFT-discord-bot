import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

os.environ['MPLCONFIGDIR'] = '/tmp'
axis_size = 24
plot_title_size = 36

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

def plotFloorDepth(floor_val_arr, floor_depth_arr, slug):
    """
    Plot the floor depth in range.

    Args:
        floor_val_arr ([type]): [description]
        floor_depth_arr ([type]): [description]
        slug ([type]): [description]
    """
    plt.style.use('ggplot')
    
    plt.rcParams['font.size'] = '16'
    x_axis = ["floor", "1.2x", "1.4x", "1.6x", "1.8x", "2.0x"]
    plt.figure(figsize=(24,16))
    plt.bar(x_axis, 
            floor_depth_arr, 
            color ='maroon',
            width = 0.4)

    plt.xlabel("Depth Upper Bound (multiple of floor)", fontsize=axis_size)
    plt.ylabel("# of Items", fontsize=axis_size)
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.title(f"Cumulative Floor Depths for {slug}", fontsize=plot_title_size)
    plt.tight_layout() # Add space at top
    plt.grid()
    plt.savefig("temp_plots/floor_depth_chart.png")
    plt.close()

    return

def priceRarityGraph(asset_df, asset_rarities, slug, floor):
    """
    Input: Rarities of each item and each item price.
    Output: Price to rarity graph.
    """
    plt.style.use('ggplot')
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
               s=100, alpha=0.8, edgecolors="k")

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

    ax.set_title(f"Price to Rarity Scores of {slug}", fontsize=plot_title_size)
    ax.set_ylabel("Rarity Score", fontsize=axis_size, fontweight='bold')
    ax.set_xlabel("Price", fontsize=axis_size, fontweight='bold')

    # label with id.
    def label_point(x, y, val, ax):
        a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
        for i, point in a.iterrows():
            ax.text(point['x']+.02, point['y'], str(point['val']), fontsize=14)

    # call label function
    label_point(nonfloor_filtered_result["price"], nonfloor_filtered_result["rarity"], nonfloor_filtered_result["id"], plt.gca())  
    plt.tight_layout() # Add space at top
    plt.grid()
    plt.savefig("temp_plots/price_rarity_plot.png")
    plt.close()

    return

### All below are from http://adilmoujahid.com/posts/2021/06/data-mining-meebits-nfts-python-opensea/

def plotTransactionVolume(df, slug):
    """
    Plot the transaction volume history for the last 30 days in terms of number of transactions

    Args:
        df - the dataframe of transactions in the last 30 days
        slug - the project slug
    """
    plt.style.use('ggplot')
    
    data = df[['timestamp', 'total_price']].resample('D', on='timestamp').count()['total_price']
    ax = data.plot.bar(figsize=(24, 16))

    ax.set_title(f"30-day Trailing Number of {slug} Sales Per Day ", fontsize=plot_title_size)
    ax.set_ylabel(f"Number of {slug} Sales", fontsize=axis_size, fontweight='bold')
    ax.set_xlabel("Date", fontsize=axis_size, fontweight='bold')

    #https://github.com/pandas-dev/pandas/issues/1918
    plt.gca().xaxis.set_major_formatter(plt.FixedFormatter(data.index.to_series().dt.strftime("%d %b")))

    #https://robertmitchellv.com/blog-bar-chart-annotations-pandas-mpl.html
    for i in ax.patches:
        # get_x pulls left or right; get_height pushes up or down
        ax.text(i.get_x(), i.get_height()+1, \
                str(round((i.get_height()), 2)), fontsize=14, color='black')
    
    plt.savefig("temp_plots/transaction_history.png")
    plt.close()
    
    return

def plotTransactionSalesETH(df, slug):
    """
    Plot the total sales per day in ETH

    Args:
        df - the dataframe of transactions in last 30 days
        slug - the project slug
    """
    plt.style.use('ggplot')
    
    data = df[['timestamp', 'total_price']].resample('D', on='timestamp').sum()['total_price']
    ax = data.plot(figsize=(24, 16), color="red", linewidth=2, marker='o', markerfacecolor='grey', markeredgewidth=0)

    ax.set_title(f"30-day Trailing Total {slug} Sales (ETH)", fontsize=plot_title_size)
    ax.set_ylabel("Sales in ETH", fontsize=axis_size, fontweight='bold')
    ax.set_xlabel("Date", fontsize=axis_size, fontweight='bold')

    dates = list(data.index)
    values = list(data.values)

    for i, j in zip(dates, values):
        text = np.round(j, 2)
        ax.annotate(f"{text}", xy=(i, j), rotation=45, fontsize=18)
    
    plt.savefig("temp_plots/transaction_sales_eth.png")
    plt.close()
    
    return


def plotAvgPrices(df, slug):
    """
    Plot the average sale price per day in ETH
    """
    data = df[['timestamp', 'total_price']].resample('D', on='timestamp').mean()['total_price']
    ax = data.plot(figsize=(24,16), color="green", linewidth=2, marker='o', markerfacecolor='grey', markeredgewidth=0)

    ax.set_title(f"30-day Trailing Average {slug} Price (ETH)", fontsize=plot_title_size)
    ax.set_ylabel("Average Price in ETH", fontsize=axis_size, fontweight='bold')
    ax.set_xlabel("Date", fontsize=axis_size, fontweight='bold')

    dates = list(data.index)
    values = list(data.values)

    for i, j in zip(dates, values):
        text = np.round(j, 2)
        ax.annotate(f"{text }".format(), xy=(i, j), rotation=45, fontsize=18)
        
    plt.savefig("temp_plots/avg_prices.png")
    plt.close()
    
    return
    
def plotFloorPrices(df, slug):
    """
    Plot floor prices for collection
    """
    data = df[['timestamp', 'total_price']].resample('D', on='timestamp').min()['total_price']
    ax = data.plot(figsize=(24,16), color="orange", linewidth=2, marker='o', markerfacecolor='grey', markeredgewidth=0)

    ax.set_title(f"30-day Trailing Floor {slug} Price (ETH)", fontsize=plot_title_size)
    ax.set_ylabel("Floor Price in ETH", fontsize=axis_size, fontweight='bold')
    ax.set_xlabel("Date", fontsize=axis_size, fontweight='bold')

    dates = list(data.index)
    values = list(data.values)

    for d, v in zip(dates, values):
        text = np.round(v, 2)
        ax.annotate(f"{text}", xy=(d, v), rotation=45, fontsize=18)
    
    plt.savefig("temp_plots/floor_prices.png")
    plt.close()
    
    return
    
def plotMaxPrices(df, slug):
    """
    Plot max prices for collection
    """
    
    data = df[['timestamp', 'total_price']].resample('D', on='timestamp').max()['total_price']
    ax = data.plot(figsize=(24,16), color="red", linewidth=2, marker='o', markerfacecolor='grey', markeredgewidth=0)

    ax.set_alpha(0.8)
    ax.set_title(f"30-day Trailing Max {slug} Price (ETH)", fontsize=plot_title_size)
    ax.set_ylabel("Max Price in ETH", fontsize=axis_size, fontweight='bold')
    ax.set_xlabel("Date", fontsize=axis_size, fontweight='bold')

    dates = list(data.index)
    values = list(data.values)

    for i, j in zip(dates, values):
        text = np.round(j, 2)
        ax.annotate(f"{text}", xy=(i, j), rotation=45, fontsize=18)
    
    plt.savefig("temp_plots/max_prices.png")
    plt.close()
    
    return