from discord.ext import commands
import discord
from playsound import playsound
import asyncio
import os

#get unique bot and channel ids from .env file
from dotenv import load_dotenv, find_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  #must be string
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  #must be integer

#initialize bot that intents to use all discord features
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


#####################################################################################
#                                    EVENTS                                          #
#####################################################################################
@bot.event
async def on_ready():  #runs when the bot is initialized
  print('Bot is ready')
  channel = bot.get_channel(CHANNEL_ID)
  await channel.send("Hey channel, I'm JimBot and I'm cool!")


@bot.event
async def on_message(message):
  #if the message is from the bot itself, do nothing
  if (message.author == bot.user):
    return

  if ("david" in message.content.lower()):
    #check if the person saying david is in the vc
    if message.author.voice and message.author.voice.channel:
      # Connect to the voice channel that the author is in
      await message.channel.send("connecting")
      vc = await message.author.voice.channel.connect()
      await message.channel.send("done connecting")
      #vc.play(discord.FFmpegPCMAudio(
      #  'https://www.youtube.com/watch?v=VpnzssRMxYA&ab_channel=Zechal'),
      #        after=lambda e: print('done', e))
      #await asyncio.sleep(2)
      await message.channel.send("Disconnecting")
      await vc.disconnect()
      await message.channel.send("done disconnecting")
    #else:
    #nothing will happen but dont alert the channel

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


#loop and continuously run until the bot is ended
bot.run(BOT_TOKEN)
