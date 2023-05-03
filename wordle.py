from letter_state import LetterState
class Wordle:
    MAX_ATTEMPTS = 6
    WORD_LENGTH = 5
    def __init__(self, secret: str):
        self.secret: str = secret.lower()
        self.attempts = []

    def attempt(self, guess: str):
        self.attempts.append(guess)

    def guess(self, guess: str):
        results = []
        for i in range(self.WORD_LENGTH):
            char = guess[i]
            letter = LetterState(char)
            letter.in_word = char in self.secret
            letter.in_pos = char == self.secret[i]
            results.append(letter)

        return results

    def is_valid(self, guess:str):
        return len(guess) == self.WORD_LENGTH

    @property
    def is_solved(self):
        return len(self.attempts) > 0 and self.attempts[-1] == self.secret

    @property 
    def remaining_attempts(self):
        return self.MAX_ATTEMPTS-len(self.attempts)

    @property
    def can_attempt(self):
        return self.remaining_attempts > 0 and not self.is_solved
    
