from discord.ext import commands
import discord

@bot.event
async def on_ready(): #runs when the bot is initialized
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hey channel, I'm JimBot and I'm cool!") #blocking await call
