from discord.ext import commands
import discord

@bot.command()
async def hello(ctx): #argv
    await ctx.send("Hiya")

@bot.command()
async def add(ctx, *arr): #argv
    result = 0
    for i in arr:
        result += int(i)
    await ctx.send(f"Result = {result}")