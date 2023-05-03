import nextcord

def generate_blanks():
    #return a string of 5 blank emoji characters
    return "\N{WHITE MEDIUM SQUARE}" * 5

def generate_letter_embed():
    embed = nextcord.Embed(title="Wordle")
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_footer(text=
        "Reply to this message with your guesses to play wordle."
    )
    return embed 

def generate_color_embed():
    embed = nextcord.Embed(title="Wordle")
    embed.description = "\n".join([generate_blanks()]*6)
    embed.set_footer(text=
        "Reply to this message with your guesses to play wordle."
    )
    return embed 