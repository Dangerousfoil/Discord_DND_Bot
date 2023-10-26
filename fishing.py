import discord
import random
import math
from tinydb import TinyDB, Query
from discord.ext import commands

animal_database = TinyDB("databases/animal_database.json")
animal_database.default_table_name = "Animal_Database"
user = Query()


class Fishing(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.biome = ""
        self.selected_weapon = ""
        self.track_success = []
        self.track_failure = []
        self.fish_success = []
        self.biome_options = ["Arctic Water", "Freshwater", "Saltwater"]
        self.weapons = {
            "1": "bow",
            "2": "spear",
            "3": "javelin",
            "4": "fishing rod",
            "5": "net",
        }

    @commands.command(name="fish")
    async def run(self, ctx):
        # Gets biome from user & starting point for command
        while True:
            embed = discord.Embed(
                title="**Fishing**",
                description="**Please enter the biome you're fishing in:**\n"
                "**-Arctic Water**\n**-Freshwater**\n"
                "**-Saltwater**\n",
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
            self.track_success.clear()
            await self.selection_fish(ctx)
        else:
            self.file_track_failure()
            failure_response = random.choice(self.track_failure)
            embed = discord.Embed(
                title="**No Signs of Life**",
                description=failure_response,
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)
            self.track_failure.clear()

    async def selection_fish(self, ctx):
        fish = animal_database.search(user.Biome == self.biome)
        prey_dict = random.choice(fish)
        prey = prey_dict.get("Name")
        print(prey, prey_dict.get("Weight"))

        match prey:
            case "Sardines":
                num_sardines = random.randint(10, 100)
                weight_sardines = prey_dict.get("Weight") * num_sardines
                prey_weight = int(weight_sardines)
            case _:
                prey_weight = random.randint(1, prey_dict.get("Weight"))

        random_num = random.randint(0, prey_weight)
        while True:
            if random_num <= prey_weight:
                embed = discord.Embed(
                    title="**Fishing**",
                    description=f"**You spot {prey}!**\n\n*To successfully catch the {prey}, "
                    f"please enter your Survival or Nature skill modifier:*",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)

            try:
                skill_modifier = int(response.content)
                break
            except ValueError:
                embed = discord.Embed(
                    title="**Invalid Input**",
                    description="*Invalid response. Please enter a valid integer value for your skill modifier.*",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
        skill_check = random.randint(1, 20) + skill_modifier
        while True:
            if skill_check >= prey_dict.get("DC"):
                embed = discord.Embed(
                    title="**Fishing Success**",
                    description=f"**You Rolled: {skill_check} = "
                    f"({skill_check - skill_modifier} + "
                    f"{skill_modifier})\nYou successfully caught a "
                    f"{prey}!\n\nChoose the fishing method used:**\n"
                    f"1. Bow\n2. Spear\n3. Javelin\n4. Fishing Rod\n"
                    f"5. Net",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title="**Fishing Failure**",
                    description=f"**You Rolled: {skill_check} = "
                    f"({skill_check - skill_modifier} + "
                    f"{skill_modifier})\nYou have failed to catch "
                    f"the {prey} and it gets away.**",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)
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
                    description="**Invalid Input. Please choice a method"
                    " from the provided list.**",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                continue

            await self.reward(ctx, prey_weight, prey)
            break

    async def reward(self, ctx, weight, prey):
        if prey == "Sardines" and self.selected_weapon != "net":
            embed = discord.Embed(
                title="**Fishing Failure**",
                description=f"**Wrong Method:** *You need a net to catch " f"{prey}*",
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)
        else:
            meat_percentage = (0.15, 0.40)
            scale_percentage = 0.02

            meat_weight = weight * random.uniform(
                meat_percentage[0], meat_percentage[1]
            )
            meat_weight = max(1, math.ceil(meat_weight))

            scale_weight = weight * scale_percentage
            scale_weight = max(1, math.ceil(scale_weight))

            meat_reward = f"**Meat:** *{meat_weight} lbs*"
            scale_reward = f"**Scales:** *{scale_weight} pieces*"

            # Get fishing success response from file
            self.file_fishing_success()
            fish_response = random.choice(self.fish_success)

            embed = discord.Embed(
                title="**Fishing Results**",
                description=f"*{fish_response}*",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name=f"**Information**",
                value=f"**Species:** *{prey}*\n**Weight:** *{weight} lbs*\n**Method:**"
                f" *{self.selected_weapon.title()}*",
                inline=False,
            )
            embed.add_field(
                name=f"**Rewards**",
                value=f"{meat_reward}\n{scale_reward}\n\n*Please discuss with your "
                f"DM to determine specific rewards and quantities*\n",
                inline=False,
            )
            await ctx.reply(embed=embed)
            self.fish_success.clear()

    def file_track_success(self):
        # Opens/reads and then stores file associated with the selected biome for success responses
        with open(
            f"fish_txt/{self.biome.lower()}_track_success.txt", encoding="utf-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.track_success.append(response)

    def file_track_failure(self):
        # Opens/reads and then stores file associated with the selected biome for fail responses
        with open(
            f"fish_txt/{self.biome.lower()}_track_failure.txt", encoding="utf-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.track_failure.append(response)

    def file_fishing_success(self):
        with open(
            f"fish_txt/{self.biome.lower()}_fish_success.txt", encoding="utf-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.fish_success.append(response)
