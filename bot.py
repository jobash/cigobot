import os
import logging
import discord
import asyncio
import giphy_client
import random
import finnhub
import requests

from giphy_client.rest import ApiException
from pprint import pprint
from dotenv import load_dotenv
from discord.ext import commands

api_instance = giphy_client.DefaultApi()

load_dotenv()
logging.basicConfig(level=logging.INFO)

token = os.getenv('DISCORD_TOKEN')
finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB'))
giphy_token = os.getenv('GIPHY')

bot = commands.Bot(command_prefix='!')
api_instance = giphy_client.DefaultApi()

@bot.command(name="gif", brief="Random gif", help="Random gif", usage="dance", case_insensitive=True)
async def gif(ctx, *args):
    query = ' '.join(args)
    try:
        response = api_instance.gifs_search_get(giphy_token, query, limit=10)
        lst = list(response.data)
        gif = random.choices(lst)

        await ctx.send(gif[0].url)

    except ApiException as e:
        logging.error(e)

@bot.command(name="stock", brief="Show price for stock", usage="GME", help="Shows current price for stock", case_insensitive=True)
async def stock(ctx, *args):
    ticker = args[0].upper()
    res = finnhub_client.quote(ticker)
    await ctx.send(res['c'])

def getPlayHelpText():
    files = os.listdir('./audio')
    filenames = [os.path.splitext(file)[0] for file in files]
    return "The following audio choices are available: \n" + '\n'.join(filenames)

@bot.command(name="avanza", brief="Show Swedish stock prices", usage="nordea", help="Shows prices of stocks that match query", case_insensitive=True)
async def avanza(ctx, *args):
    query = ' '.join(args)
    resultList = []
    try:
        response = requests.get('https://www.avanza.se/_cqbe/search/global-search/global-search-template?query=' + query)
        resultGroups = response.json()['resultGroups']
        for resultGroup in resultGroups:
            if resultGroup['instrumentType'] == "STOCK":
                hits = resultGroup['hits']
                for hit in hits:
                    resultList.append("{}: {} {}\n".format(hit['link']['linkDisplay'], hit['lastPrice'], hit['currency']))
        message = "The following stocks were found:\n" + ''.join(resultList)
        await ctx.send(message)
    except Exception as e:
        logging.error(e)



@bot.command(name="play", brief="Play audio", usage="amg", help=getPlayHelpText(), case_insensitive=True)
async def play(ctx, arg):
    user = ctx.author
    if user.voice == None:
        await ctx.send("Join a voice channel first")
        return

    voice_channel = user.voice.channel
    logging.info(f"voice channel {voice_channel}")

    file_path = f"./audio/{arg.lower()}.mp3"
    if not os.path.isfile(file_path):
        await ctx.send("Audio file not found")
        return
    

    vc = await voice_channel.connect()
    vc.play(discord.FFmpegPCMAudio(file_path))
    while vc.is_playing():
        await asyncio.sleep(1)
    vc.stop()
    await vc.disconnect()

bot.run(token)