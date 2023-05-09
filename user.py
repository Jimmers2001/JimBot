class User:
    def __init__(self, name, balance=420, wordle_wins=0, times_exercised=0):
        self.name: str = name
        self.balance: int = balance
        self.wordle_wins: int = wordle_wins
        self.times_exercised: int = times_exercised
        self.inventory = []
        self.xp: int = 0
    
    def newUser(self, d):
        self.name: str = d["name"]
        self.balance: int = d["balance"]
        self.wordle_wins: int = d["wordle_wins"]
        self.times_exercised: int = d["times_exercised"]
        self.inventory = d["inventory"]
        self.xp: int = d["xp"]

    def deposit(self, amount: int):
        if amount <= 0:
            print("cant deposit", amount)
            return
        self.balance += amount

        
    def withdraw(self, amount: int):
        if amount <= 0 or amount > self.balance:
            print("cant withdraw", amount)
            return
        self.balance -= amount
        
    def print_attributes(self):
        print(f"Name: {self.name}")
        print(f"Balance: {self.balance}")
        print(f"Wordle Wins: {self.wordle_wins}")
        print(f"Times Exercised: {self.times_exercised}")
        print(f"Inventory: {self.inventory}")
        print(f"XP: {self.xp}")
