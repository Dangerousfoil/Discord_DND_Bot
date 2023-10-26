import discord
import random
import math
from tinydb import TinyDB, Query
from discord.ext import commands

# Sets up variables for database access
animal_database = TinyDB("databases/animal_database.json")
animal_database.default_table_name = "Animal_Database"
user = Query()


class Hunting(commands.Cog):
    """
    Simulates hunting in different biomes with various animals for each biome. And calculates the
    amount of meat and hide collected from each animal based on the animals weight. Allows players
    to select a weapon to kill the animal with.
    """

    def __init__(self, bot):
        # Declares variables/lists/dictionaries for use in the class
        self.client = bot
        self.biome = ""
        self.selected_weapon = ""
        self.track_success = []
        self.track_failure = []
        self.hunt_success = []
        self.biome_options = ["Arctic", "Desert", "Grassland", "Woodland", "Tundra"]
        self.weapons = {
            "1": "bow",
            "2": "crossbow",
            "3": "spear",
            "4": "javelin",
            "5": "sling",
        }

    @commands.command(name="hunt")
    async def run(self, ctx):
        # Gets biome from user & starting point for command
        while True:
            embed = discord.Embed(
                title="**Hunting**",
                description="**Please enter the biome you're hunting in:**\n"
                            "**-Arctic**\n**-Desert**\n**-Grassland**\n"
                            "**-Woodland**\n**-Tundra**",
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)

            # Check to make sure the bot is interacting with the user that called the command
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)
            self.biome = response.content.title()
            # Checks user input against biome_options list
            if self.biome not in self.biome_options:
                embed = discord.Embed(
                    title="**Invalid Biome**",
                    description=f"**{self.biome.title()} is not a valid biome. "
                                f"Please enter a valid biome.**",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
            else:
                break
        await self.success_check(ctx)

    async def success_check(self, ctx):
        # Checks if user successfully finds signs of life (75% chance of success)
        if random.randint(1, 4) <= 3:
            self.file_track_success()
            success_response = random.choice(self.track_success)
            embed = discord.Embed(
                title="**Signs of Life**",
                description=success_response,
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)
            await self.selection_hunt(ctx)
        else:
            self.file_track_failure()
            failure_response = random.choice(self.track_failure)
            embed = discord.Embed(
                title="**No Signs of Life**",
                description=failure_response,
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)

    async def selection_hunt(self, ctx):
        # Pulls all animals for the selected biome from the database and puts them in a list
        animals = animal_database.search(user.Biome == self.biome)
        prey_dict = random.choice(animals)
        prey = prey_dict.get("Name")
        prey_weight = random.randint(1, prey_dict.get("Weight"))
        random_num = random.randint(0, prey_weight - 1)
        while True:
            if random_num < prey_weight:
                embed = discord.Embed(
                    title="**Animal Tracking**",
                    description=f"**You found {prey} tracks!**\n\n*To successfully "
                                f"track and hunt a {prey}, please enter your "
                                f"Survival or Nature skill modifier:*",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)

                # Check to make sure the bot is interacting with the user that called the command
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    response = await self.client.wait_for("message", check=check)
                    skill_modifier = int(response.content)
                    break
                except ValueError:
                    embed = discord.Embed(
                        title="**Invalid Response**",
                        description="**Invalid Input! Please enter a valid integer "
                                    "value for your skill modifier.**",
                        color=discord.Color.red(),
                    )
                    await ctx.reply(embed=embed)
        skill_check = random.randint(1, 20) + skill_modifier
        while True:
            if skill_check >= prey_dict.get("DC"):
                embed = discord.Embed(
                    title="**Animal Tracking Success**",
                    description=f"**You Rolled: {skill_check} =** "
                                f"**({skill_check - skill_modifier} + {skill_modifier})**\n"
                                f"**You successfully tracked and hunted a {prey}!\n\n**",
                    color=discord.Color.blue(),
                )
                embed.add_field(
                    name="**Choose the hunting method used:**\n",
                    value="**1. Bow\n2. Crossbow\n3. Spear\n4. Javelin\n5. Sling**",
                )
                await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="**Hunting Failure**",
                    description=f"**You Rolled:** *{skill_check} = "
                                f"({skill_check - skill_modifier} + {skill_modifier})*\n"
                                f"**You failed to track and hunt the {prey}!\n\n**",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)

            # Check to make sure the bot is interacting with the user that called the command
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)

            # Assign the correct weapon depending on user input
            try:
                for key, value in self.weapons.items():
                    if response.content == key:
                        x = self.weapons.get(response.content)
                        self.selected_weapon = x
                        break
                    elif response.content == value:
                        self.selected_weapon = response.content
                        break
                else:
                    raise ValueError
            except ValueError:
                embed = discord.Embed(
                    title="**Invalid Input**",
                    description="**Invalid Input. Please enter a valid weapon choice.**",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                continue

            await self.reward(ctx, prey_weight, prey)
            break

    async def reward(self, ctx, weight, prey):
        # Percentages for meat and hide given to player as reward
        meat_percentage = (0.15, 0.40)
        hide_percentage = 0.02

        # Calculates the amount of meat to give to the player
        meat_weight = weight * random.uniform(meat_percentage[0], meat_percentage[1])
        meat_weight = max(1, math.ceil(meat_weight))

        # Calculates the amount of hide to give to the player
        hide_weight = weight * hide_percentage
        hide_weight = max(1, math.ceil(hide_weight))

        meat_reward = f"**Meat:** *{meat_weight} lbs*"
        hide_reward = f"**Hide:** *{hide_weight} pieces*"

        # Gets hunt success response from file
        self.file_success()
        hunt_response = random.choice(self.hunt_success)

        embed = discord.Embed(
            title="**Hunting Results**",
            description=f"*{hunt_response}*",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=f"**Information**",
            value=f"**Species:** *{prey}*\n**Weight:** *{weight} lbs*\n**Method:** "
                  f"*{self.selected_weapon.title()}*",
            inline=False,
        )
        embed.add_field(
            name=f"**Rewards**",
            value=f"{meat_reward}\n{hide_reward}\n\n*Please discuss with your DM "
                  f"to determine specific rewards and quantities*\n",
            inline=False,
        )
        await ctx.reply(embed=embed)
        self.hunt_success.clear()

    def file_track_success(self):
        # Opens/reads and then stores file associated with the selected biome for success responses
        with open(f"hunt_txt/{self.biome}_track_success.txt", encoding="utf-8") as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.track_success.append(response)

    def file_track_failure(self):
        # Opens/reads and then stores file associated with the selected biome for fail responses
        with open(f"hunt_txt/{self.biome}_track_failure.txt", encoding="utf-8") as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.track_failure.append(response)

    def file_success(self):
        # Opens/reads and then stores file associated with the selected biome for hunt responses
        with open(f"hunt_txt/{self.biome}_hunt_success.txt", encoding="utf-8") as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.hunt_success.append(response)
