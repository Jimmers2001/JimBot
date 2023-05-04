#from discord.ext import commands
#import discord
from playsound import playsound
#from discord import FFmpegPCMAudio
import asyncio
import os
from replit import db
from keep_alive import keep_alive
import random
import nextcord
from nextcord.ext import commands
#from play_wordle import play_wordle
from wordle import *
#get unique bot and channel ids from .env file
from dotenv import load_dotenv, find_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  #must be string
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  #must be integer
GUILD_ID = int(os.getenv("GUILD_ID"))

#initialize bot that intents to use all discord features
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
      
#empty db and initialize all users with $1000
async def initialize_db(guild):
    db.clear() #emptying it loses all data
    for member in guild.members:
        db[member.name] = 420
        if member.id == bot.user.id:
            db[member.name] = 0
    sorted(db, reverse=True)


#####################################################################################
#                                    EVENTS                                         #
#####################################################################################

#runs when the bot is first initialized
@bot.event
async def on_ready():  
    print('Bot is ready')
    channel = bot.get_channel(CHANNEL_ID)
    guild = bot.get_guild(GUILD_ID)

    #only run initialize_db on the first time the bot runs on the server
    if len(db.keys()) == 0:
        await channel.send("Hey channel, I'm JimBot and I'm cool!")
        await initialize_db(guild) #only wanna initialize once, if ever ran again it erases everything

#runs every time a message is sent
@bot.event
async def on_message(message):
    #if the message is from the bot itself, do nothing
    if (message.author == bot.user):
        return

    if 'kyle' in message.content.lower():
        await message.add_reaction('\U0001F913')  # nerd face emoji

    if 'jim' in message.content.lower() and not 'jimbot' in message.content.lower():
        await message.add_reaction('\U0001F60E')  # sunglasses emoji

    if (False and "david" in message.content.lower()):
        #check if the person saying david is in the vc
        if message.author.voice and message.author.voice.channel:
            # Connect to the voice channel that the author is in
            await message.channel.send("connecting")
            vc = await message.author.voice.channel.connect()
            await message.channel.send("done connecting")

            #vc.play(nextcord.FFmpegPCMAudio('testing.mp3'), after=lambda e: print('done', e))
            #vc.is_playing()
            #vc.pause()
            #vc.resume()
            #vc.stop()

            #await vc.play(nextcord.FFmpegPCMAudio(
            #  'https://www.youtube.com/watch?v=VpnzssRMxYA&ab_channel=Zechal'),
            #        after=lambda e: print('done', e))
            #await asyncio.sleep(2)
            await message.channel.send("Disconnecting")
            await vc.disconnect()
            await message.channel.send("done disconnecting")
        #else:
        #nothing will happen but dont alert the channel


########################
#        WORDLE        #
########################
    ref = message.reference
    #if the message is a reply (has a refernece) 
    if ref and isinstance(ref.resolved, nextcord.Message):
        parent = ref.resolved

        #message isnt a reply to a bot or message has no embeds
        if parent.author.id != bot.user.id or not parent.embeds:
            return
        
        #make sure its a wordle embed and not another
        if "wordle" in parent.embeds[0].title.lower():        
            letter_embed = parent.embeds[0]
            color_embed = parent.embeds[1]

            #check that the correct user is playing the game
            if color_embed.author.name != message.author.name:
                await message.reply(f"Get your own game bruh, {color_embed.author.name} is in the middle of clutching up.", delete_after=3)
                try:
                    await message.delete(delay=3)
                except Exception:
                    pass
                return

            #check that the game is not over
            if is_game_over(color_embed):
                await message.reply("The game is over. Start a new game with !wordle", delete_after=3)
                try:
                    await message.delete(delay=3)
                except Exception:
                    pass
                return

            #check that the word is valid
            if len(message.content.split()) > 1:
                await message.reply(f"Given {message.content}. Please only enter one 5 letter word.", delete_after = 3)
                try:
                    await message.delete(delay=3)
                except Exception:
                    pass
                return
            if not is_valid_word(message.content):
                await message.reply(f"{message.content} is not a valid guess", delete_after = 3)
                try:
                    await message.delete(delay=3)
                except Exception:
                    pass
                return

            #update the embed
            new_letter_embed = update_letter_embed(letter_embed, message.content) 
            new_color_embed = update_color_embed(color_embed, message.content) 
            await parent.edit(embeds=[new_letter_embed, new_color_embed])

            #delete the message
            try:
                await message.delete()
            except Exception:
                pass
            
            #check if the field "winnings" is defined
            if len(new_color_embed.fields) > 0:
                ctx = await bot.get_context(message)
                await bank_update_db(ctx, int(new_color_embed.fields[0].value))

    #MUST HAVE PROCESS_COMMANDS so other commands can be done as well
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(error)


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
#               CONNECTIONS              #
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
    amount = arr[1] #ignore the rest of arr arguments

    #confirm the amount is valid
    if not amount.isnumeric():
        await ctx.channel.send("Invalid amount: " + amount)
        return
    amount = int(arr[1])

    if giver == receiver:
        await ctx.channel.send("Cannot pay yourself " + giver)
        return
    if not giver in db.keys():
        await ctx.channel.send("Could not find your account: " + giver)
        return
    if not receiver in db.keys():
        await ctx.channel.send("Could not find account: " + receiver)
        return
    if amount <= 0:
        await ctx.channel.send("Must give positive amount to " + receiver)
        return

    #check if the giver has enough to give
    if db[giver] > amount:
        #assume giver and receiver both have bank accounts
        db[giver] -= amount
        db[receiver] += amount
        embed = nextcord.Embed(
            title = ":moneybag: Transaction :moneybag:",
            description = giver + " gave $" + str(amount) + " to " + receiver,
            color=nextcord.Color.green()
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

@bot.command(description="Play a game of wordle")
async def wordle(interaction: nextcord.Interaction):
    #generate a puzzle
    puzzle_id = random_puzzle_id()

    #create the puzzle to display: a letter only and color only board (need custom emojis to combine)
    letter_embed = generate_empty_embed(interaction.author, puzzle_id)
    color_embed = generate_empty_embed(interaction.author, puzzle_id)

    #send the puzzle as an interaction 
    instructions="Reply to this message with your guesses to play wordle."
    await interaction.send(content=instructions, embeds=[letter_embed, color_embed])
    
"""
@bot.command()
#example: !play blackjack 100
async def play(ctx, *arr):
    game = arr[0]

    #check for games that dont involve bets
    if game.strip().lower() == "wordle":

        await play_wordle(ctx, *arr)
        return

    #continue with games that do have bets
    bet = arr[1]
    if not bet.isnumeric():
        await ctx.channel.send("Invalid bet amount: " + bet)
        return
    bet = int(arr[1])

    if db[ctx.author.name] < bet:
        await ctx.channel.send(str(ctx.author.name) + " has insufficient funds to bet $" + str(bet))
        return

    await ctx.channel.send(str(ctx.author.name) + " is playing " + game + " with bet " + str(bet))
    #for now, just always win and double the bet
    await bank_update_db(ctx, bet)
"""
@bot.command(aliases=['agent'])
async def pick(ctx):
    agents = ["Brimstone", "Viper", "Omen", "Killjoy", "Cypher", "Phoenix", "Sova",
        "Sage", "Jett", "Reyna", "Raze", "Breach", "Skye", "Yoru", "Astra", "KAYO",
        "Chamber", "Neon", "Fade", "Harbor", "Gekko"]
    agent = random.choice(agents)
    await ctx.channel.send(str(ctx.author.name) + " should play " + agent)

@bot.command(aliases=['flipcoin', 'coinflip', 'coin'])
async def flip(ctx):
    coin = random.choice(['Heads', 'Tails'])
    await ctx.send(f"{coin}!")

#loop and continuously run until the bot is ended
keep_alive() #creates a replit url that we constantly ping using uptimerobot to keep the bot active and running
bot.run(BOT_TOKEN)
