import random

if input("Rock, paper, or scissors? ").lower() in ["rock", "paper", "scissors"]:
    print(random.choice(["You lose!", "Tie!", "You win!"]))
else:
    print("You dunce!")
