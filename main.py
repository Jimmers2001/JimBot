#from playsound import playsound
#from discord import FFmpegPCMAudio
import asyncio, nextcord, os, replit, random
from keep_alive import keep_alive
from nextcord.ext import commands, tasks
from wordle import *
#from user import *
from dotenv import load_dotenv
import os 

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  #must be string
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  #must be integer
GUILD_ID = int(os.getenv("GUILD_ID"))
REPLIT_DB_URL = os.getenv("REPLIT_DB_URL")
db = replit.database.Database(REPLIT_DB_URL)

#slot_emojis:str = ["🍒", "🍊", "🍋", "🍉", "🍇", "🍎", "🍓", "🍑", "🍍"]
slot_emojis = [":toilet:"]*130 + [":gem:"]*10 + [":watermelon:"]*50 + [":strawberry:"]*50 + [":hot_pepper:"]*30 + [":kiwi:"]*50 + [":cherries:"]*100 + [":grapes:"]*30 + [":peach:"]*30 + [":pineapple:"]*50 + [":avocado:"]*30 + [":tomato:"]*50 + [":eggplant:"]*30 + [":broccoli:"]*20 + [":carrot:"]*30 + [":corn:"]*30 + [":cucumber:"]*30 + [":potato:"]*50 + [":leafy_green:"]*50 + [":mushroom:"]*50 + [":onion:"]*50 + [":garlic:"]*50
if len(slot_emojis) != 1000:
    print("length of slot_emojis is ", len(slot_emojis))

#initialize bot that intents to use all discord features
bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())
bot.remove_command('help') #remove the default help and replace it with my own later

def print_dictionary(d:dict) -> dict:
    """Prints a dictionary in a prettier format"""
    for key, value in d.items():
        print(f"{key}: {value}")
    print("\n")


def make_dictionary(name:str, balance=420, wordle_wins=0, times_exercised=0, inventory=[], xp=0) -> dict:
    """Creates and returns a dictionary representing a user"""
    d = dict()
    d["name"] = name
    d["balance"] = balance
    d["wordle_wins"] = wordle_wins
    d["times_exercised"] = times_exercised
    d["inventory"] = inventory
    d["xp"] = xp
    return d

#empty db and initialize all users with money
def initialize_db(guild):
    """Empties and initializes a db entry of dictionaries for each user"""
    db.clear() #emptying it loses all data
    for member in guild.members:
        d = dict()
        if member.id == bot.user.id:
            d = make_dictionary(member.name, 1000, 0, 1000)
            #give huge inventory and stuff to the bot####################################
        else:
            d = make_dictionary(member.name) #give starter items#########################

        db[member.name] = d

async def delete_message(ctx, delay):
    try:
        await ctx.message.delete(delay=delay)
    except Exception as e:
        print("Could not delete the original message.", e)

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
        initialize_db(guild) #only wanna initialize once, if ever ran again it erases everything

    #print("DATABASE:")
    # Loop through the list and print each pair
    #for id, user in db.items():
    #    print(id)
    #    print_dictionary(user)

#runs every time a message is sent
@bot.event
async def on_message(message):
    """Executes operations on a message by message basis, including wordle"""
    #if the message is from the bot itself, do nothing
    if (message.author == bot.user):
        return

    if 'kyle' in message.content.lower() or message.author == "jelloman639#0298":
        await message.add_reaction('\U0001F913')  # nerd face emoji

    if 'jim' in message.content.lower() and not 'jimbot' in message.content.lower():
        await message.add_reaction('\U0001F60E')  # sunglasses emoji


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
            ctx = await bot.get_context(message)    
            letter_embed = parent.embeds[0]
            color_embed = parent.embeds[1]
            keyboard_embed = parent.embeds[2]

            should_delete = False
            #check that the correct user is playing the game
            if color_embed.author.name != message.author.name:
                await message.reply(f"Get your own game bruh, {color_embed.author.name} is in the middle of clutching up.", delete_after=10)
                should_delete = True

            #check that the game is not over
            if is_game_over(color_embed):
                await message.reply("The game is over. Start a new game with !wordle", delete_after=10)
                should_delete = True

            #check that the word is valid
            if len(message.content.split()) > 1:
                await message.reply(f"Given {message.content}. Please only enter one 5 letter word.", delete_after = 3)
                should_delete = True
                
            if not is_valid_word(message.content):
                await message.reply(f"{message.content} is not a valid guess", delete_after = 3)
                should_delete = True

            if should_delete:
                await delete_message(ctx, 10)
                return

            #update the embed
            new_letter_embed = update_letter_embed(letter_embed, message.content) 
            new_color_embed = update_color_embed(color_embed, message.content) 
            new_keyboard_embed = update_keyboard_embed(keyboard_embed, message.content)
            await parent.edit(embeds=[new_letter_embed, new_color_embed, new_keyboard_embed])

            #delete the message
            await delete_message(ctx, 1)
            
            #check if the field "winnings" is defined
            if len(new_color_embed.fields) > 0:
                await bank_update_db(ctx.author.name, int(new_color_embed.fields[0].value), ctx)

    #MUST HAVE PROCESS_COMMANDS so other commands can be done as well
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(error, delete_after=10)
        await delete_message(ctx, 10)

#####################################################################################
#                                    COMMANDS                                       #
#####################################################################################

@bot.command(description="I'll let you figure that out")
async def help(ctx, *, command=None): #* forces command to be a "keyword" type and helps with error checking
    # If a specific command is passed as an argument, print out only its description text
    if command:
        cmd = bot.get_command(command)
        if not cmd:
            await ctx.send(f"Command '{command}' not found.", delete_after=10)
            await delete_message(ctx, 10)
            return
        embed = nextcord.Embed(title=f"{command} Command description", description=cmd.description, color=0x00ff00)
        await ctx.send(embed=embed, delete_after=60)
        await delete_message(ctx, 10)
        return

    # If no command is passed, print out a list of all commands and their description text
    embed = nextcord.Embed(title="Command List", color=0x00ff00)
    for cmd in bot.commands:
        embed.add_field(name=f"**{cmd.name}**", value=cmd.description or "No description available", inline=False)
    await ctx.send(embed=embed, delete_after=600)

@bot.command(description="greets you")
async def hello(ctx):  #argv
    print("in hello")
    greetings: str = "Hello, Hi, Hey, Yo, What's up, Greetings, Salaam, Namaste, Bonjour, \
        Hola, Ciao, Konnichiwa, Ni hao, Merhaba, Sawubona, Shalom, Hallo, Privet, Ahlan, Sveiki,\
        Zdravstvuyte, Kia ora, Xin chào, Selamat pagi, Marhaba, Kumusta, Sannu, Dumelang, \
        Jambo, Bawoni, Sawatdee, Saumia, Habari, Dumela, Shwmae, Hi, 嘿，你這個男孩, \
        Hey there, Mornin', Howdy, G'day, Wazzapnin, Yo., Hiya, Whats good, Whats up, \
        Howdy, Salut, Moin, Hoi, Ola, Ciao, Merhaba, Sawubona, Përshëndetje, Bok, Kumusta, Sveiki, Labas, \
        Sholem aleikhem, Hallo, Salve, Ahoj, Hej, Dobrý den, Marhabaan, Yasou, Hei, Sannu, Nǐ hǎo, Terve,\
        Hejhej, Aksunai, Dia dhuit, Dobro jutro, Dzień dobry, Xaipete, Salamu alaikum, Mirëdita,\
        Sannu da zuwa, Zdravstvuyte, Shwmae, Moïen, Sveikas, Moi, Moien, Goede dag, Moïen, Szia,\
        Hej alla, Nǐn hǎo, Hejhej, Привет, Xayrli tong, Cześć, Merhabalar, Hello"

    await ctx.send(random.choice(greetings.split(", ")))


@bot.command(description="adds a list of numbers")
async def add(ctx, *arr):  #argv
    result = 0
    for i in arr:
        result += int(i)
    await ctx.send(f"Result = {result}", delete_after=60)
    await delete_message(ctx, 60)


##########################################
#               CONNECTIONS              #
##########################################

@bot.command(pass_context=True, description="invites the bot to join the call")
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("Joined the voice channel", delete_after=10)
        await delete_message(ctx, 10)

    else:
        await ctx.send("You are not in a voice channel", delete_after=10)
        await delete_message(ctx, 10)        


@bot.command(pass_context=True, description="disconnects the bot from the call", aliases=['disconnect', 'die', 'kill'])
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Left the voice channel", delete_after=10)
    
    else:
        await ctx.send("Cannot leave the voice channel since I am not in one.", delete_after=10)
        await delete_message(ctx, 10)

##########################################
#               FINANCES                 #
##########################################

#add amount to a user's bank account
async def bank_update_db(id:str, amount:int, ctx=None):
    """Adds amount to the user's bank account"""
    original_bal = 0
    if id in db.keys():
        original_bal = db[id]["balance"]
        db[id]["balance"] += amount
    else:
        #only happens if a user joins after the bot started running
        #so in practice should be never
        db[id]["balance"] += 420 + amount

    if original_bal > 0 and db[id]["balance"] < 0 and ctx:
        await ctx.channel.send(":crab: " + str(ctx.author.name) + " has gone bankrupt! :crab:")

@bot.command(description="displays the bank accounts of all users", aliases=['lb', 'blb', 'bank_leaderboard'])
async def leaderboard(ctx):
    if (len(db.keys()) == 0):
        #should never happen
        await ctx.channel.send("No bank users yet", delete_after=10)
        await delete_message(ctx, 10)
        return
    
    #make embedded message
    embed = nextcord.Embed(title="Leaderboard", color=0xff0000)
    index = 1
    sorted_users = sorted(db.items(), key=lambda x: x[1]["balance"], reverse=True)
    for _, user in sorted_users:
        n = user["name"]
        b = user["balance"]
        embed.add_field(name=f"{index}. {n}", value=f"${b}", inline=False)
        index += 1
    
    await ctx.send(embed=embed)

    await delete_message(ctx, 10)
    return

@bot.command(description="displays your bank account balance", aliases=['bal'])
async def balance(ctx):
    await ctx.channel.send(ctx.author.name + " has $" + 
                           str(db[ctx.author.name]["balance"]) + " :money_with_wings:", delete_after=600)
    await delete_message(ctx, 600)

@bot.command(description="pay another user with !pay <user> <amount>")
#example: !pay Jimmers2001 100
async def pay(ctx, *arr):
    #check for receiver and amount info
    if len(arr) < 2:
        await ctx.send("Please provide <user> <amount> information.")
        return
    giver = ctx.author.name
    receiver = arr[0]
    amount = arr[1] #ignore the rest of arr arguments

    #confirm the amount is valid
    if not amount.isnumeric():
        await ctx.channel.send("Invalid amount: " + amount, delete_after=10)
        await delete_message(ctx, 10)
        return
    amount = int(arr[1])

    bad_command = False
    if giver == receiver:
        await ctx.channel.send("Cannot pay yourself " + giver, delete_after=10)
        bad_command=True
    if not giver in db.keys():
        await ctx.channel.send("Could not find your account: " + giver, delete_after=10)
        bad_command=True
    if not receiver in db.keys():
        await ctx.channel.send("Could not find account: " + receiver, delete_after=10)
        bad_command=True
    if amount <= 0:
        await ctx.channel.send("Must give positive amount to " + receiver, delete_after=10)
        bad_command=True

    if bad_command:
        await delete_message(ctx, 10)
        return

    #check if the giver has enough to give
    if db[giver]["balance"] > amount:
        #assume giver and receiver both have bank accounts
        await bank_update_db(giver, -amount, ctx)
        await bank_update_db(receiver, amount, ctx)

        embed = nextcord.Embed(
            title = ":moneybag: Transaction :moneybag:",
            description = giver + " gave $" + str(amount) + " to " + receiver,
            color=nextcord.Color.green()
        )

        await ctx.channel.send(embed=embed)
        await delete_message(ctx, 10)
        return

    else:
        await ctx.channel.send(giver + " is too *poor* to give $" + str(amount) + " to " + receiver + "\n(i dont talk to broke boys)", delete_after=10)
        await delete_message(ctx, 10)
        return


##########################################
#               GAMES                    #
##########################################

@bot.command(description="workout for money (you could use it)", aliases=['pushups', 'squats'])
async def exercise(ctx): 
    await ctx.channel.send(str(ctx.author.name) + " has to do 10 pushups/squats for $50", delete_after=60)
    await asyncio.sleep(40)
    await ctx.channel.send(str(ctx.author.name) + " better have done 10 pushups/squats... here's $50! :muscle:")
    await bank_update_db(ctx.author.name, 50, ctx)
    await delete_message(ctx, 10)
    
@bot.command(description="play wordle")
async def wordle(interaction: nextcord.Interaction):
    #generate a puzzle
    puzzle_id = random_puzzle_id()

    #create the puzzle to display: a letter only and color only board (need custom emojis to combine)
    letter_embed = generate_empty_embed(interaction.author, puzzle_id)
    color_embed = generate_empty_embed(interaction.author, puzzle_id)
    keyboard_embed = generate_keyboard_embed(interaction.author)

    #send the puzzle as an interaction 
    instructions="Reply to this message with your guesses to play wordle."
    await interaction.send(content=instructions, embeds=[letter_embed, color_embed, keyboard_embed])
    #unable to delete the original message in the interaction


class SlotView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
    
    @nextcord.ui.button(label="Spin again")
    async def on_button_click(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        new_embed = nextcord.Embed(title="Jim Spins", color=nextcord.Color.green())
        new_embed.set_author(name=interaction.user.name, icon_url=str(interaction.user.avatar.url))
        new_embed.description = spin()

        #instead of having add_field, just reset the description by doing description=spin()
        await interaction.response.edit_message(embed=new_embed, view=self)
        #await interaction.response.defer() #i think this makes the discord bot look like its typing. Good for waiting for an API 

    """async def on_button_click(self, interaction: nextcord.Interaction, button: nextcord.ui.Button):
        ctx = await self.bot.get_context(interaction)
        print("in on_button_click")
        if button.custom_id == 'slot_button':
            #spin again
            print("spin again")
            await spin(ctx)"""

async def calc_winnings(d: str):
    print(d)
    return 0

async def spin():
    #the 3 rows
    d = random.choice(slot_emojis)+random.choice(slot_emojis)+random.choice(slot_emojis)+"\n\n"
    d += random.choice(slot_emojis)+random.choice(slot_emojis)+random.choice(slot_emojis)+"\n\n"
    d += random.choice(slot_emojis)+random.choice(slot_emojis)+random.choice(slot_emojis)+"\n"
    
    #reward based on the outcome
    winnings = await calc_winnings(d)
    bank_update_db(winnings)

    return d

@bot.command(description="play slots")
async def slots(ctx, *arr):
    #check bet logic
    if len(arr) < 1:
        await ctx.send("Please provide the amount you are betting (!slots <amount>).", delete_after=3)
        await delete_message(ctx, 3)
        return
    
    bet = arr[0]

    if not bet.isnumeric() or int(bet) <= 0:
        await ctx.send("Invalid bet amount: " + bet, delete_after=3)
        await delete_message(ctx, 3)
        return
    bet = int(bet)

    if db[ctx.author.name] < bet:
        await ctx.send(str(ctx.author.name) + " has insufficient funds to bet $" + str(bet), delete_after=3)
        await delete_message(ctx, 3)
        return

    # Shuffle the emojis to simulate a slot machine
    random.shuffle(slot_emojis)

    # Construct the slot machine message
    message = nextcord.Embed(title="Jim Spins", color=nextcord.Color.green())
    message.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    
    #start by randomly choosing the emojis and then edit later to choose a location in the array and loop through to show the animation
    
    message.description = spin()

    # Send the message to the channel where the command was invoked
    await ctx.send(embed=message, view=SlotView())
    

@bot.command()
#example: !play blackjack 100
async def play(ctx, *arr):
    game = arr[0]

    #check for games that dont involve bets
    if game.strip().lower() == "wordle":
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

@bot.command(description="randomly choose an agent", aliases=['pick'])
async def agent(ctx):
    agents = ["Brimstone", "Viper", "Omen", "Killjoy", "Cypher", "Phoenix", "Sova",
        "Sage", "Jett", "Reyna", "Raze", "Breach", "Skye", "Yoru", "Astra", "KAYO",
        "Chamber", "Neon", "Fade", "Harbor", "Gekko"]
    agent = random.choice(agents)
    await ctx.channel.send(str(ctx.author.name) + " should play " + agent, delete_after=90)
    await delete_message(ctx, 10)

@bot.command(description="flip a coin", aliases=['flipcoin', 'coinflip', 'coin'])
async def flip(ctx):
    coin = random.choice(['Heads', 'Tails'])
    await ctx.send(f"{coin}!", delete_after=60)
    await delete_message(ctx, 30)

#loop and continuously run until the bot is ended
keep_alive() #creates a replit url that we constantly ping using uptimerobot to keep the bot active and running
bot.run(BOT_TOKEN)
