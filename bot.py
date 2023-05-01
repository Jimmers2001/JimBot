from discord.ext import commands
import discord

#get unique bot and channel ids from .env file
#from dotenv import load_dotenv
#load_dotenv()

#initialize bot that intents to use all discord features
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready(): #runs when the bot is initialized
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hey channel, I'm JimBot and I'm cool!") #blocking await call

@bot.command()
async def hello(ctx): #argv
    await ctx.send("Hiya")

@bot.command()
async def add(ctx, *arr): #argv
    result = 0
    for i in arr:
        result += int(i)
    await ctx.send(f"Result = {result}")

#loop and continuously run until the bot is ended
bot.run(BOT_TOKEN)