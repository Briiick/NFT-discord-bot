# import libraries
from pkgutil import iter_modules
import pandas as pd
import os
import numpy as np
import discord
from scrape_assets import getOneAssetData
from scrape_collection import collectionStatsQuery
from scrape_events import eventQuery
from kpi_calculations import floorDepthCalc, inTheMoney, pricedAtGain, buyersellerCalc
from graphing import rarityScoring, plotFloorDepth, priceRarityGraph, plotTransactionVolume, plotTransactionSalesETH, plotAvgPrices, plotFloorPrices, plotMaxPrices
from discord_req import discordUserQuery
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import logging
#import dataframe_image as dfi

# SET UP LOGGER
logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# settings
# sys.path.append('../')
# sns.set()
# np.set_printoptions(suppress=True)
load_dotenv(".env")
# environment variables

# set up discord client
client = discord.Client()

# when client is ready, output message.
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# check message
@client.event
async def on_message(message):
    """
    Function to run when a message is sent.

    Args:
        message - the message sent
    Outputs help or analysis based upon message send (!scan or !help).
    """
    if message.author == client.user:
        return
    
    # take content of message
    msg = message.content
    
    # check beginning of message
    if msg.startswith('!scan'):
        slug = msg[6:] # parse everything after !scan
        
        ### GATHER DATA
        await message.channel.send(f"**Gathering collection data for {slug}.**")
        collection_df, discord_url = collectionStatsQuery(slug) # get collection data
        if collection_df.empty: # if it's empty then something went wrong.
            await message.channel.send(f"{slug} Not found on OpenSea. Check the slug and resubmit.")
        else:
            await message.channel.send(f"Link to collection: https://opensea.io/collection/{slug}")
            await message.channel.send(f"Collection details: \n")
            
            ### output collection details to discord across rows
            # collection_df transpose
            collection_df_t = collection_df.T
            #dfi.export(collection_df_t, 'dataframe_images/collection_stats.png')
            await message.channel.send(collection_df_t.to_string(justify='center'))
                
            ### DISCORD NUMBER OF USERS
            try:
                discord_num_users = discordUserQuery(discord_url)
                await message.channel.send(f"Number of Discord users = {discord_num_users}")
            except:
                pass
            
            ### HOLDER-TO-ITEM RATIO
            holder_to_item = round(float(collection_df['num_owners'] / total_tokens), 2)
            number_owners = int(collection_df['num_owners'])
            await message.channel.send(f"Holders-to-items ratio: {number_owners}/{total_tokens} = {holder_to_item}")
            
            # gather total tokens
            total_tokens = int(collection_df['total_supply'])
            await message.channel.send(f"**Gathering asset data for {slug}...**")
            # tell how long will take
            if total_tokens <= 10000:
                await message.channel.send(f"There are {total_tokens} assets to query. This won't take too long.")
            elif 10000 < total_tokens <= 20000:
                await message.channel.send(f"There are {total_tokens} assets to query. This will take 5-10 minutes.")
            elif 20000 < total_tokens <= 50000:
                await message.channel.send(f"There are {total_tokens} assets to query. This will take 10-20 minutes.")
            else:
                await message.channel.send(f"There are {total_tokens} assets to query. This is a lot of assets. This will take a while.")
            # get asset data
            asset_df, asset_data = getOneAssetData(slug, total_tokens)
            #print(len(asset_df))

            ### CALCULATE FLOOR
            floor = float(collection_df[collection_df['collection_name'] == slug]['floor_price'])
            
            ### PASSION INTENSITY
            passion_intensity = inTheMoney(floor, asset_df)
            await message.channel.send(f"{slug} owners in the money = {passion_intensity}%")

            ### SENTIMENT SCORE
            sentiment_score = pricedAtGain(floor, asset_df)
            await message.channel.send(f"{slug} items priced at a gain = {sentiment_score}%")
            
            ### FLOOR DEPTH
            floor_val_arr, floor_depth_arr = floorDepthCalc(floor, asset_df)
            plotFloorDepth(floor_val_arr, floor_depth_arr, slug)
            await message.channel.send(file=discord.File('temp_plots/floor_depth_chart.png'))

            ### PRICERARITYGRAPH
            asset_rarities = rarityScoring(asset_data, total_tokens, slug)
            priceRarityGraph(asset_df, asset_rarities, slug, floor)
            await message.channel.send(file=discord.File('temp_plots/price_rarity_plot.png'))
            
            ### TRANSACTION GRAPHS
            await message.channel.send(f"**Gathering 30-day trailing transaction data for {slug}...**")
            transaction_df = eventQuery(slug)
            await message.channel.send(f"There are %d unique {slug} sellers." % len(transaction_df['seller_address'].unique()))
            await message.channel.send(f"There are %d unique {slug} buyers." % len(transaction_df['buyer_address'].unique()))
            # top buyers and sellers
            buyer_df = buyersellerCalc(transaction_df, buyer=True)
            #dfi.export(buyer_df, 'dataframe_images/buyer_df.png')
            await message.channel.send(f"**The top {slug} buyers (30-day trailing) are:**")
            await message.channel.send(buyer_df.to_string())
            seller_df = buyersellerCalc(transaction_df, buyer=False)
            #dfi.export(seller_df, 'dataframe_images/seller_df.png')
            await message.channel.send(f"**The top {slug} sellers (30-day trailing) are**:")
            await message.channel.send(seller_df.to_string())
            
            # transaction volume
            plotTransactionVolume(transaction_df, slug)
            await message.channel.send(file=discord.File('temp_plots/transaction_history.png'))
            # transaction sales ETH
            plotTransactionSalesETH(transaction_df, slug)
            await message.channel.send(file=discord.File('temp_plots/transaction_sales_eth.png'))
            # average prices ETH
            plotAvgPrices(transaction_df, slug)
            await message.channel.send(file=discord.File('temp_plots/avg_prices.png'))
            # floor prices ETH
            plotFloorPrices(transaction_df, slug)
            await message.channel.send(file=discord.File('temp_plots/floor_prices.png'))
            # max prices ETH
            plotMaxPrices(transaction_df, slug)
            await message.channel.send(file=discord.File('temp_plots/max_prices.png'))
            

            await message.channel.send(f"Note, if you want to understand these metrics, type **!help**")
            
    
    elif msg.startswith('!help'):
        await message.channel.send("***Commands:*** \n\
Type !scan <end of OpenSea URL> to get started. \n\
\n\
***KPI info:*** \n\
**Floor depth:** The number of items currently listed at a price below X and the current floor  (i.e. how many floor items traded it would take to raise the floor price by X%). This KPI indicates how much upward price resistance exists for a given collection – the thinner the floor, the easier the upward motion. \n\
\n\
**Owners in the money:** The percentage of items currently listed for sale that would make money if listed at the current floor price (i.e. the floor price of the collection is higher than the item’s last traded price). This KPI indicates conviction – how many people are selling off their NFTs now that they have made money vs. holding for future. The higher the percentage, the less conviction. \n\
\n\
**Priced at a gain:** The percentage of items currently listed for sale that are priced at a gain (i.e. the list price of an item is higher than its last traded price). This KPI indicates the market’s current feelings about a collection – the higher the score, the more optimistic holders may be about being able to turn a profit.")

client.run(os.getenv("TOKEN"))
