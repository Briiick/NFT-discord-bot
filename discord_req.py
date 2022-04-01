import requests
from bs4 import BeautifulSoup
import re

def discordUserQuery(url):
    """
    Input the discord url
    Return the number of users.
    """
    headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }
    
    # get the html
    req = requests.get(url, headers)
    # use bs4 to parse
    soup = BeautifulSoup(req.content, 'html.parser')
    # collect metadata (specifically description)
    discord_metadata = soup.find("meta", property="og:description").get('content')
    # parse out comma from integer
    no_comma_discord_desc = re.sub(",", "", discord_metadata)
    # collect number of users
    num_discord_users = [float(s) for s in re.findall(r'-?\d+\.?\d*', no_comma_discord_desc)]
    
    return int(num_discord_users[0])