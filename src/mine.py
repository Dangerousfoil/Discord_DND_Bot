import discord
import random
from tinydb import TinyDB, Query
from discord.ext import commands

special_material_database = TinyDB("databases/special_material_database.json")
special_material_database.default_table_name = "Special_Material_Database"
user = Query()


class Mine(commands.Cog):
    """
    Simulates mining for metal ore in different biomes. Uses a percent chance to determine the
    amount of metal ore harvested per cycle. Gives players flavor text to successful or failed
    attempts.
    """

    def __init__(self, bot):
        # Declares variables/lists/dictionaries for use in class
        self.client = bot
        self.biome, self.modifier_input = "", 0
        self.success_response, self.failure_response = [], []
        self.success_tiers = [1.0, 0.10, 0.05]
        self.biome_options = ["arctic", "desert", "grassland", "tundra", "woodland"]
        self.amount = {"metal": {1: 1, 2: 1, 3: 1}}

    @commands.command(name="mine")
    async def mine_start(self, ctx):
        # Gets biome from user & starting point for command
        embed = discord.Embed(
            title="**Mining**",
            description="**Please enter the biome you're mining in:**\n\n"
            "**-Arctic**\n**-Desert**\n**-Grassland**\n**-Woodland**"
            "\n**-Tundra**",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Performs check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.biome = response.content.lower()
        # Checks user input against biome list
        if self.biome not in self.biome_options:
            embed = discord.Embed(
                title="**Invalid Biome**",
                description=f"**{self.biome.title()} is not a recognized biome."
                f" Please enter a valid biome.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.mine_start(ctx)
        else:
            await self.tool_confirmation(ctx)

    async def tool_confirmation(self, ctx):
        # Checks if the user is in the right location and has teh proper tool to harvest metal
        embed = discord.Embed(
            title="**Mining**",
            description="**Do you have a Pickaxe and are you near a "
            f"harvestable source of metal?**\n\n**Yes/No**",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        tool_input = response.content.lower()

        match tool_input:
            case "yes":
                await self.strength_modifier(ctx)
            case _:
                embed = discord.Embed(
                    title="**Unable To Mine**",
                    description="**You can't gather metal without proper"
                    " tools or without being near a harvestable "
                    "source of metal. "
                    " Mining ends.**",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)
                await self.tool_confirmation(ctx)

    async def strength_modifier(self, ctx):
        # Gets strength or dexterity modifier from user as input
        embed = discord.Embed(
            title="**Modifier**",
            description="**Please provide your Strength or Dexterity " "modifier:**",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        
        try:
            self.modifier_input = int(response.content)
            await self.result(ctx)
        except ValueError:
            embed = discord.Embed(
                title="**Invalid Input**",
                description="**Invalid input, please provide a valid integer.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.strength_modifier(ctx)

    @staticmethod
    def special_metals(biome):
        # Adds a randomly selected "special" metal based on weights
        special_metal_options = special_material_database.search(
            user.Group.all([biome.title(), "Metal"])
        )
        special_metal = random.choices(
            special_metal_options, weights=[0.05, 0.025, 0.0125]
        )
        choice = special_metal[0]["Name"]
        return choice

    async def result(self, ctx):
        extra_metal = self.special_metals(self.biome)
        # Displays the results for the mining attempts and displays the result
        num_gathered = 0
        success_count = 0
        # Loops through success_chance and multiplies it by the self.modifier_input provided
        for tier, success_chance in enumerate(self.success_tiers, start=1):
            modified_chance = success_chance * self.modifier_input

            if random.random() <= modified_chance:
                success_count += 1
                num_gathered += self.amount["metal"][tier]

        # If gathering is successful displays the amount of metal gained
        if num_gathered > 0:
            self.file_success()
            select_response = random.choice(self.success_response)
            embed = discord.Embed(
                title="**Mining Success**", color=discord.Color.blue()
            )
            embed.add_field(
                name="**Result**", value=f"*{select_response}*", inline=False
            )
            embed.add_field(name="**Time Taken**", value="*2hrs*", inline=False)
            embed.add_field(
                name="**Note**", value=f"*{num_gathered}x metal gathered*", inline=False
            )
            embed.add_field(
                name="**Special Material**",
                value=f"*1x {extra_metal.title()} was found while you were mining."
                "\n\n\nPlease contact your DM to add the metal amounts listed*",
            )
            await ctx.reply(embed=embed)
        else:
            self.file_failure()
            select_response = random.choice(self.failure_response)
            embed = discord.Embed(title="**Mining Failed**", color=discord.Color.blue())
            embed.add_field(
                name="**Result**", value=f"*{select_response}*", inline=False
            )
            await ctx.reply(embed=embed)

    def file_success(self):
        # Read metal success response file depending on the biome selected
        with open(
            f"gather_txt/{self.biome}_metal_response.txt", encoding="utf-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.success_response.append(response)

    def file_failure(self):
        # Reads metal failure response file depending on the biome selected
        with open(
            f"gather_txt/f_{self.biome}_metal_response.txt", encoding="uft-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.failure_response.append(response)
