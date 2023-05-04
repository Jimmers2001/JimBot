import random
import nextcord
from nextcord.ext import commands

popular_words = open("popular-5-letter-words.txt").read().splitlines()
all_words = set(word.strip() for word in open("sowpods.txt"))

EMOJI_CODES = {
    "green": ":green_square:",

    "gray": ":black_large_square:",

    "yellow": ":yellow_square:",

    "a": ":regional_indicator_a:",
    "b": ":regional_indicator_b:",
    "c": ":regional_indicator_c:",
    "d": ":regional_indicator_d:",
    "e": ":regional_indicator_e:",
    "f": ":regional_indicator_f:",
    "g": ":regional_indicator_g:",
    "h": ":regional_indicator_h:",
    "i": ":regional_indicator_i:",
    "j": ":regional_indicator_j:",
    "k": ":regional_indicator_k:",
    "l": ":regional_indicator_l:",
    "m": ":regional_indicator_m:",
    "n": ":regional_indicator_n:",
    "o": ":regional_indicator_o:",
    "p": ":regional_indicator_p:",
    "q": ":regional_indicator_q:",
    "r": ":regional_indicator_r:",
    "s": ":regional_indicator_s:",
    "t": ":regional_indicator_t:",
    "u": ":regional_indicator_u:",
    "v": ":regional_indicator_v:",
    "w": ":regional_indicator_w:",
    "x": ":regional_indicator_x:",
    "y": ":regional_indicator_y:",
    "z": ":regional_indicator_z:"
}

#make an empty row
def generate_blanks() -> str:
    #return a string of 5 blank emoji characters
    return "\N{WHITE MEDIUM SQUARE}" * 5

#make an entirely empty board
def generate_empty_embed(user: nextcord.User, puzzle_id: int) -> nextcord.Embed:
    embed = nextcord.Embed(title="Wordle")
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(text=f"ID: {puzzle_id}")
    return embed

#check if a word is valid
def is_valid_word(word: str) -> bool:
    word = word.replace(" ", "").replace("\n", "").replace("\t", "").lower()

    #quick check to not need to search through all_words
    if len(word) != 5:
        return False
    return word in all_words

#checks if the game is over
def is_game_over(embed: nextcord.Embed) -> bool:
    #\n\n is only written in the update_color_embed as the final message when the game is over
    return "\n\n" in embed.description

#choose one of the words from the popular words list
def random_puzzle_id() -> int:
    return random.randint(0,len(popular_words)-1)

#produce a list of colors ["gray", "gray", "green", "yellow", "yellow"]
def generate_colored_word(guess: str, answer: str) -> list:
    colored_letters = ["gray", "gray", "gray", "gray", "gray"]
    guess_letters = list(guess)
    answer_letters = list(answer)

    #change colors to green for same letter and same place
    for i in range(len(guess_letters)):
        if guess_letters[i] == answer[i]:
            colored_letters[i] = "green"
            answer_letters[i] = None
            guess_letters[i] = None

    #change colors to yellow for same letter in wrong place
    for i in range(len(guess_letters)):
        if guess_letters[i] is not None and guess_letters[i] in answer_letters:
            colored_letters[i] = "yellow"
            answer_letters[answer_letters.index(guess_letters[i])] = None
    return colored_letters

#converts the inputted list of inputs into a string of emojis
def generate_emojis(input: list) -> str:
    emojis = ""
    for word in input:
        #they represent colors like "gray", "yellow", or "green"
        if len(input) > 1:
            emojis += EMOJI_CODES[word]

        #it represents a character in a word
        else:
            for letter in word:
                emojis += EMOJI_CODES[letter]
    
    return emojis

#updates the embed that only has letters
def update_letter_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    #convert the guess into emojis
    letter_emojis = generate_emojis([guess])
    empty_slot = generate_blanks()

    #replace the next blank found with the guess as emojis
    embed.description = embed.description.replace(empty_slot, letter_emojis, 1)
    return embed

#updates the embed that has colors 
def update_color_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    #use the id to figure out the answer
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]

    #convert the guess into gray, yellow, or green strings
    colored_word_list = generate_colored_word(guess, answer)

    #convert the colored_word_list strings into emojis
    colored_emojis = generate_emojis(colored_word_list)
    empty_slot = generate_blanks()

    #replace the first blank with the colored word
    embed.description = embed.description.replace(empty_slot, colored_emojis, 1)

    #check for game over using remaining guesses
    remaining_guesses = embed.description.count(empty_slot)
    money_made = 0
    if guess == answer:
        if remaining_guesses == 0:
            embed.description += "\n\nClose call Bozo, you kinda suck..."
            money_made = 1
        elif remaining_guesses == 1:
            embed.description += "\n\nYou are not built different, you are mid..."
            money_made = 5
        elif remaining_guesses == 2:
            embed.description += "\n\nBet."
            money_made = 10
        elif remaining_guesses == 3:
            embed.description += "\n\nBIIIIIIIIG :100: :fire: :weary: :sweat_drops:"
            money_made = 20
        elif remaining_guesses == 4:
            embed.description += "\n\nMOM GET THE CAMERA!"
            money_made = 100
        elif remaining_guesses == 5:
            embed.description += "\n\ncheck him pc, VAC alert"
            money_made = 1000
        embed.description += f"\nYou got the answer! It was {answer}."
    elif guess != answer and remaining_guesses == 0:
        embed.description += f"\n\nThe answer was {answer}. You're on the bench now."
    
    #amount of money made from wordle
    embed.add_field(name="winnings", value=money_made)

    return embed