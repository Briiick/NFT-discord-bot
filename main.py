# import libraries
import pandas as pd
import os
import numpy as np
import discord
from scrape_assets import getOneAssetData
from scrape_collection import collectionStatsQuery
from kpi_calculations import floorDepthCalc, passionIntensityCalc, sentimentScoreCalc
from graphing import rarityScoring, priceRarityGraph
import matplotlib.pyplot as plt
from dotenv import load_dotenv

# settings
# sys.path.append('../')
# sns.set()
# np.set_printoptions(suppress=True)
load_dotenv()
# environment variables

# set up discord client
client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith('!scan'):
        slug = msg[6:]
        
        ### GATHER DATA
        await message.channel.send(f"**Gathering collection data for {slug}.**")
        collection_df = collectionStatsQuery(slug)
        if not collection_df.empty:
            await message.channel.send(f"Link to collection: https://opensea.io/collection/{slug}")
            await message.channel.send(f"Collection details: \n")
            for i, j in collection_df.iterrows():
                await message.channel.send(f"{i}, {j} \n")
            await message.channel.send(f"**Gathering asset data for {slug}.**")
            asset_df, asset_data = getOneAssetData(slug, int(collection_df['total_supply']))

            ### CALCULATE FLOOR
            floor = float(collection_df[collection_df['collection_name'] == slug]['floor_price'])
            
            ### FLOOR DEPTH
            floor_depth = floorDepthCalc(floor, asset_df)
            await message.channel.send(f"Floor Depth for {slug} = {floor_depth} items")

            ### PASSION INTENSITY
            passion_intensity = passionIntensityCalc(floor, asset_df)
            await message.channel.send(f"Floor > Previous for {slug} = {passion_intensity}%")

            ### SENTIMENT SCORE
            sentiment_score = sentimentScoreCalc(floor, asset_df)
            await message.channel.send(f"Current > Previous for {slug} = {sentiment_score}%")
            
            ### PRICERARITYGRAPH
            asset_rarities = rarityScoring(asset_data, slug)
            priceRarityGraph(asset_df, asset_rarities, slug)
            await message.channel.send(file=discord.File('current_plot.jpg'))

            await message.channel.send(f"Note, if you want to understand these metrics, type **!help**")

        else:
            await message.channel.send(f"{slug} Not found on OpenSea.")
    
    elif msg.startswith('!help'):
        await message.channel.send("***KPI info:*** \n\
**Floor Depth:** The number of items currently listed at a price below 1.5x the current floor  (i.e. how many floor items traded it would take to raise the floor price by 50%). This KPI indicates how much upward price resistance exists for a given collection – the thinner the floor, the easier the upward motion. \n\
\n\
**Floor > Previous:** The percentage of items currently listed for sale that would make money if listed at the current floor price (i.e. the floor price of the collection is higher than the item’s last traded price). This KPI indicates conviction – how many people are selling off their NFTs now that they have made money vs. holding for future. The higher the percentage, the less conviction. \n\
\n\
**Current > Previous:** The percentage of items currently listed for sale that are priced at a gain (i.e. the list price of an item is higher than its last traded price). This KPI indicates the market’s current feelings about a collection – the higher the score, the more optimistic holders may be about being able to turn a profit.")

client.run(os.getenv('TOKEN'))
