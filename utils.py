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

def generate_letter_embed(puzzle_id: int):
    embed = nextcord.Embed(title="Wordle")
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_footer(text=
        f"ID: {puzzle_id} | Reply to this message with your guesses to play wordle."
    )
    return embed 

def generate_color_embed(puzzle_id: int):
    embed = nextcord.Embed(title="Wordle")
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

#produce a list of colors ["gray", "gray", "green", "yellow", "yellow"] and will eventually hand of that list to the generate_color_embed
def generate_colored_word(guess: str, answer: str) -> str:
    colored_letters = ["gray" for letter in guess]
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
    print("".join(colored_letters))
    return "".join(colored_letters)

def update_embed(embed: nextcord.Embed, guess: str) -> nextcord.Embed:
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]
    colored_word = generate_colored_word(guess, answer)
    empty_slot = generate_blanks()

    #replace the first blank with the colored word
    embed.description = embed.description.replace(empty_slot, colored_word, 1)
    return embed