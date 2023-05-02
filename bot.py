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

#####################################################################################
#                                    EVENTS                                         #
#####################################################################################
@bot.event
async def on_ready():  #runs when the bot is initialized
    print('Bot is ready')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hey channel, I'm JimBot and I'm cool!")
    
    guild = bot.get_guild(GUILD_ID)
    #await initialize_db(guild) #only wanna initialize once, if ever ran again it erases everything


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


##########################################
#               CONNECTION               #
##########################################

@bot.command(pass_context=True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel")


@bot.command(pass_context=True, aliases=['disconnect', 'die', 'kill'])
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left the voice channel")
    else:
        await ctx.send("Cannot leave the voice channel since I am not in one.")


##########################################
#               FINANCES                 #
##########################################

#add amount to a user's bank account
async def bank_update_db(ctx, amount):
    user = str(ctx.author.name)
    original_bal = 0
    if user in db.keys():
        original_bal = db[user]
        db[user] += amount
    else:
        #only happens if a user joins after the bot started running
        #so in practice should be never
        db[user] = 1000 + amount

    if original_bal > 0 and db[user] < 0:
      await ctx.channel.send(":crab: " + user + " has gone bankrupt! :crab:")

@bot.command(aliases=['blb', 'leaderboard'])
async def bank_leaderboard(ctx):
    if (len(db.keys()) == 0):
       await ctx.channel.send("No bank users yet")
       return
    for i in db.keys():
        user = i
        amount = db[user]
        await ctx.channel.send(user + " has $" + str(amount))

@bot.command(aliases=['bal'])
async def balance(ctx):
    await ctx.channel.send(ctx.author.name + " has $" + 
                           str(db[ctx.author.name]) + " :money_with_wings:")

@bot.command()
#example: !pay Jimmers2001 100
async def pay(ctx, *arr):
    giver = ctx.author.name
    receiver = arr[0]
    amount = int(arr[1])

    if giver == receiver:
        await ctx.channel.send("Cannot pay yourself " + giver)
        return
    if not giver in db.keys():
        await ctx.channel.send("Could not find account: " + giver)
        return
    if not receiver in db.keys():
        await ctx.channel.send("Could not find account: " + receiver)
        return
    if amount < 0:
        await ctx.channel.send("Cannot give negative amount to " + receiver)
        return

    #check if the giver has enough to give
    if db[giver] > amount:
        #assume giver and receiver both have bank accounts
        db[giver] -= amount
        db[receiver] += amount
        embed = discord.Embed(
            title = ":moneybag: Transaction :moneybag:",
            description = giver + " gave $" + str(amount) + " to " + receiver,
            color=discord.Color.green()
        )

        await ctx.channel.send(embed=embed)

    else:
        await ctx.channel.send(giver + " is too poor to give $" + str(amount) + " to " + receiver)
        return
    


##########################################
#               GAMES                    #
##########################################
@bot.command(aliases=['pushup', 'squats'])
async def pushups(ctx): 
    await ctx.channel.send(str(ctx.author.name) + " has to do 10 pushups/squats for $50")
    await asyncio.sleep(30)
    await ctx.channel.send(str(ctx.author.name) + " better have done 10 pushups/squats... here's $50! :muscle:")
    await bank_update_db(ctx, 50)



@bot.command()
#example: !play blackjack 100
async def play(ctx, *arr):
    game = arr[0]
    bet = int(arr[1])

    if db[ctx.author.name] < bet:
        await ctx.channel.send(str(ctx.author.name) + " has insufficient funds to bet $" + str(bet))
        return

    await ctx.channel.send(str(ctx.author.name) + " is playing " + game + " with bet " + str(bet))
    #for now, just always win and double the bet
    await bank_update_db(ctx, bet)

@bot.command(aliases=['agent'])
async def pick(ctx):
    agents = ["Brimstone", "Viper", "Omen", "Killjoy", "Cypher", "Phoenix", "Sova",
        "Sage", "Jett", "Reyna", "Raze", "Breach", "Skye", "Yoru", "Astra", "KAYO",
        "Chamber", "Neon", "Fade", "Harbor", "Gekko"]
    agent = random.choice(agents)
    await ctx.channel.send(str(ctx.author.name) + " should play " + agent)

@bot.command(aliases=['coinflip', 'coin'])
async def flip(ctx):
    coin = random.choice(['Heads', 'Tails'])
    await ctx.send(f"{coin}!")

#loop and continuously run until the bot is ended
keep_alive() #creates a replit url that we constantly ping using uptimerobot to keep the bot active and running
bot.run(BOT_TOKEN)
