from discord.ext import commands
import discord
from playsound import playsound
import asyncio
import os
from replit import db
from keep_alive import keep_alive
import random

#get unique bot and channel ids from .env file
from dotenv import load_dotenv, find_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  #must be string
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  #must be integer
GUILD_ID = int(os.getenv("GUILD_ID"))

#initialize bot that intents to use all discord features
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
      
#empty db and initialize all users with $1000
async def initialize_db(guild):
    db.clear() #emptying it loses all data
    for member in guild.members:
        if member.id == bot.user.id:
            continue
        db[member.name] = 1000
    sorted(db, reverse=True)

#add amount to a user's bank account
async def bank_update_db(ctx, amount):
    user = str(ctx.author.name)
    if user in db.keys():
        db[user] += amount
    else:
        #only happens if a user joins after the bot started running
        db[user] = 1000 + amount

    if amount < 0:
      await ctx.channel.send(user + " has gone bankrupt!")

#####################################################################################
#                                    EVENTS                                         #
#####################################################################################
@bot.event
async def on_ready():  #runs when the bot is initialized
    print('Bot is ready')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hey channel, I'm JimBot and I'm cool!")
    
    guild = bot.get_guild(GUILD_ID)
    await initialize_db(guild) #only wanna initialize once, if ever ran again it erases everything


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
async def hello(ctx):  #argv
    await ctx.send("Hiya")


@bot.command()
async def add(ctx, *arr):  #argv
    result = 0
    for i in arr:
        result += int(i)
    await ctx.send(f"Result = {result}")


@bot.command(pass_context=True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel")


@bot.command(pass_context=True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left the voice channel")
    else:
        await ctx.send("Cannot leave the voice channel since I am not in one.")

@bot.command(aliases=['blb'])
async def bank_leaderboard(ctx):
    if (len(db.keys()) == 0):
       await ctx.channel.send("No bank users yet")
       return
    for i in db.keys():
        user = i
        amount = db[user]
        await ctx.channel.send(user + " has $" + str(amount))

@bot.command()
#!play blackjack 100
async def play(ctx, *arr):
    game = arr[0]
    bet = int(arr[1])
    await ctx.channel.send(str(ctx.author.name) + " is playing " + game + " with bet " + str(bet))
    #for now, just always win and double the bet
    await bank_update_db(ctx, bet)

@bot.command()
async def pick(ctx):
    agents = ["Brimstone", "Viper", "Omen", "Killjoy", "Cypher", "Phoenix", "Sova",
        "Sage", "Jett", "Reyna", "Raze", "Breach", "Skye", "Yoru", "Astra", "KAYO",
        "Chamber", "Neon", "Fade", "Harbor", "Gekko"]
    agent = random.choice(agents)
    await ctx.channel.send(str(ctx.author.name) + " should play " + agent)

@bot.command()
async def flip(ctx):
    coin = random.choice(['Heads', 'Tails'])
    await ctx.send(f"{coin}!")

#loop and continuously run until the bot is ended
keep_alive() #creates a replit url that we constantly ping using uptimerobot to keep the bot active and running
bot.run(BOT_TOKEN)
