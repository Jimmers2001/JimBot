from discord.ext import commands
import discord
import os

#get unique bot and channel ids from .env file
from dotenv import load_dotenv, find_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") #must be string
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) #must be integer

#initialize bot that intents to use all discord features
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

#####################################################################################
#                                    EVENTS                                          #
#####################################################################################
@bot.event
async def on_ready(): #runs when the bot is initialized
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hey channel, I'm JimBot and I'm cool!")

@bot.event
async def on_message(message):
    
    #if the message is from the bot itself, do nothing
    if (message.author == bot.user):
        return

    #MUST HAVE PROCESS_COMMANDS so other commands can be done as well
    await bot.process_commands(message)

    

#####################################################################################
#                                    COMMANDS                                       #
#####################################################################################
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