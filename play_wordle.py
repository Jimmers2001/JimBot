from wordle import Wordle
import random

def play_wordle():
    #load words and randomly select one
    word_set = load_words("wordle_words.txt")
    secret = random.choice(list(word_set))

    #initialize wordle game
    wordle = Wordle(secret)
    while wordle.can_attempt:
        guess = input("Type your guess: ").lower()
        guess = guess.replace(" ", "").replace("\n", "").replace("\t", "") #removes all whitespace
        if not wordle.is_valid(guess) or not guess in word_set:
            print(f"Invalid word \"{guess}\", try again!")
            continue
        wordle.attempt(guess)
        results = wordle.guess(guess)
        print(*results, sep="\n")

    #check wordle game results
    if wordle.is_solved:
        print("You got the answer!")
    else:
        print("You failed to solve the wordle!")
        print(f"The word was {secret}!")

    return 0

def load_words(path: str):
    word_set = set()
    with open(path, "r") as f:
        for line in f.readlines():
            word = line.strip().lower()
            word_set.add(word)
    return word_set


if __name__ == "__main__":
    play_wordle()