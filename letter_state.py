class LetterState:
    def __init__(self, character: str):
        self.character: str = character
        self.in_word: bool = False
        self.in_pos: bool = False

    def __repr__(self):
        return f"[{self.character} in_word: {self.in_word} in_pos: {self.in_pos}]"