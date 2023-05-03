import random
import nextcord

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

def generate_blanks():
    #return a string of 5 blank emoji characters
    return "\N{WHITE MEDIUM SQUARE}" * 5

def generate_empty_embed(puzzle_id: int):
    embed = nextcord.Embed(title="Wordle")
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_footer(text=
        f"ID: {puzzle_id} | Reply to this message with your guesses to play wordle."
    )
    return embed

#dont need
def generate_letter_embed(puzzle_id: int, guess_letters: str):
    embed = nextcord.Embed(title="Wordle")

    #SET THE DESCRIPTION TO THE GUESS IN EMOJIS
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_footer(text=
        f"ID: {puzzle_id} | Reply to this message with your guesses to play wordle."
    )
    return embed 

#dont need
def generate_color_embed(puzzle_id: int, guess_colors):
    embed = nextcord.Embed(title="Wordle")

    #SET THE DESCRIPTION TO THE GUESS IN COLORS BASED ON LOCATION
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_footer(text=
        f"ID: {puzzle_id} | Reply to this message with your guesses to play wordle."
    )
    return embed 

#check if a word is valid
def is_valid_word(word: str) -> bool:
    word = word.replace(" ", "").replace("\n", "").replace("\t", "").lower()

    #quick check to not need to search through all_words
    if len(word) != 5:
        return False
    return word in all_words

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


def generate_emojis(input: list):
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

def update_letter_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    #puzzle_id = int(embed.footer.text.split()[1])
    #answer = popular_words[puzzle_id]
    letter_emojis = generate_emojis([guess])
    empty_slot = generate_blanks()

    #replace the first blank with the guess as emojis
    embed.description = embed.description.replace(empty_slot, letter_emojis, 1)
    return embed

def is_game_over(embed: nextcord.Embed) -> bool:
    return "\n\n" in embed.description

def update_color_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]
    colored_word_list = generate_colored_word(guess, answer)
    colored_emojis = generate_emojis(colored_word_list)
    empty_slot = generate_blanks()

    #replace the first blank with the colored word
    embed.description = embed.description.replace(empty_slot, colored_emojis, 1)

    #check for game over
    remaining_guesses = embed.description.count(empty_slot)
    if guess == answer:
        if remaining_guesses == 0:
            embed.description += "\n\nClose call Bozo, you kinda suck..."
        elif remaining_guesses == 1:
            embed.description += "\n\nYou are not built different, you are mid..."
        elif remaining_guesses == 2:
            embed.description += "\n\nBet."
        elif remaining_guesses == 3:
            embed.description += "\n\nBIIIIIIIIG :100: :fire: :weary: :sweat_drops:"
        elif remaining_guesses == 4:
            embed.description += "\n\nMOM GET THE CAMERA!"
        elif remaining_guesses == 5:
            embed.description += "\n\ncheck him pc, VAC alert"
        embed.description += f"\nYou got the answer! It was {answer}."
    elif guess != answer and remaining_guesses == 0:
        embed.description += f"\n\nThe answer was {answer}. You're on the bench now."

    return embed