import os
import logging
import aiohttp
import discord
import asyncio
import giphy_client
import random
import finnhub
import openai

intents = discord.Intents.default()
intents.message_content = True
from giphy_client.rest import ApiException
from dotenv import load_dotenv
from discord.ext import commands

api_instance = giphy_client.DefaultApi()

load_dotenv()
logging.basicConfig(level=logging.INFO)

token = os.getenv('DISCORD_TOKEN')
finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB'))
giphy_token = os.getenv('GIPHY')
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

bot = commands.Bot(command_prefix='!', intents=intents)
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
        await ctx.send(e.reason)
        logging.error(e)

async def post_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json = data) as response:
            return await response.json()

@bot.command(name="cigo", brief="Ask Cigo bot", help="Ask Cigo bot", usage="What is Ronaldos catchphrase", case_insensitive=True)
async def cigo(ctx, *args):
    query = ' '.join(args)
    try:
        async with ctx.typing():
            response = await post_data("http://192.168.1.82:11434/api/generate", {
                "model": "huihui_ai/qwen3-abliterated:0.6b",
                "prompt": " /no think " + query,
                "stream": False,
                "options": {
                    "temperature": 1,
                }
            })
            answer = response["response"].replace("<think>\n\n</think>\n\n", "")
            for ans in chunkstring(answer, 2000):
                await ctx.send(ans, mention_author = True)

    except Exception as e:
        await ctx.send(e._message)
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
        response = await post_data('https://www.avanza.se/_api/search/filtered-search', {
            "originPath": "/start",
            "query": query,
            "searchFilter": {
                "types": ["STOCK"]
            },
            "pagination": {
                "from": 0,
                "size": 5
            }
        })
        hits = response['hits']
        for hit in hits:
            resultList.append("{}: {} {}\n".format(hit['title'], hit['price']['last'], hit['price']['currency']))
        message = "The following stocks were found:\n" + ''.join(resultList)
        await ctx.send(message)
    except Exception as e:
        await ctx.send(e.reason)
        logging.error(e)

@bot.command(name="to", case_insensitive=True, hidden=True)
async def to(ctx, *args):
    query = ' '.join(args)
    if query == None or query == "":
        return
    channel = discord.utils.get(ctx.guild.channels, name=query)
    if channel == None:
        return
    user = ctx.author
    await user.move_to(channel)


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

def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

bot.run(token)