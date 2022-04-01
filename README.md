# NFT Treasure Hunt: Real-Time Digital Art Valuation
## Discord Bot
### Project Description

What is the best NFT deal at any given time? How can you evaluate a project that has just been shilled to you at a conference? This project allows you to analyse collection and specific assets within collections for better visibility of the market and potential investments.

This Discord bot is used to provide more visibility into the OpenSea NFT marketplace. Rather than loading data on the backend, everything is processed ad hoc. Realistically, the NFT marketplace doesn't operate at super fast speeds. Transaction rates are generally quite slow and more methodical than making marginal second-by-second gains like a currency trader or even day trader. Thus, to wait a few minutes while data is scraped for extra visibility into a specific collection and investor might buy into, can be highly advantageous in terms of generating profit.

### Project Structure

```
├── README.md                     <- The top-level README for developers using this project.
├── requirements.txt              <- Requirements for this project.
│
├── main.py                       <- The main file for connecting to the Discord channel and processing requests.
│
├── scrape_assets.py              <- Contains utility function for scraping and processing asset data.
├── scrape_collection.py          <- Contains utility function for scraping and processing holistic collection data.
│
├── graphing.py                   <- Contains utility function for graphing data.
├── kpi_calculations.py           <- Contains utility function for calculating KPIs
├── discord_req.py                <- Contains utility function for calculating the number of Discord users.
│
├── /temp_plots                   <- Contains the temporary plots for each discord run.
```

### Additional Information

To join the Discord where you can test the bot, reach out to me at (contact info at https://bricken.co).

Feel free to fork this project, as long as you reference my work.