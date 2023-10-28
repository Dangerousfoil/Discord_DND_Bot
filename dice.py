import random


class Dice:
    def __init__(self):
        self.dice_size_options = [4, 6, 8, 10, 12, 20, 100]
        self.dice_holder = []

    def run(self):
        while True:
            dice_size = int(input("What size dice do you want to roll?"))
            dice_count = int(input("How many dice do you want to roll?"))
            user_choice = input("Would you like to roll for advantage or disadvantage?")
            if dice_size in self.dice_size_options:
                while dice_count != 0:
                    number_rolled = random.randint(1, dice_size)
                    print(f"You rolled a {number_rolled}")
                    self.dice_holder.append(number_rolled)
                    dice_count -= 1
            if user_choice == "advantage":
                self.dice_advantage()
            elif user_choice == "disadvantage":
                self.dice_disadvantage()
            else:
                print(f"{dice_size} is not a supported dice type.")
                self.run()
            self.roll_again()

    def dice_advantage(self):
        print(f"Your advantaged roll is {max(self.dice_holder)}")

    def dice_disadvantage(self):
        print(f"Your disadvantaged roll is {min(self.dice_holder)}")

    @staticmethod
    def roll_again():
        while True:
            msg = input("Do you want to roll again???")
            if msg == "no":
                quit()
            elif msg == "yes":
                break
            else:
                continue


run_dice = Dice()
run_dice.run()
