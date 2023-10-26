import discord
import random
from discord.ext import commands


class Chop(commands.Cog):
    """
    Simulates gathering wood in different biomes. Uses a percent chance to determine the amount
    of wood gathered per cycle. Gives user flavor text to successful and failed attempts
    """

    def __init__(self, bot):
        # Declares variables/lists/dictionaries for use in class
        self.client = bot
        self.biome, self.material, self.modifier_input = None, "wood", 0
        self.color = discord.Color.blue()
        self.wood_response, self.f_wood_response = [], []
        self.success_tiers = [1.0, 0.10, 0.05]
        self.special_tiers = [0.05, 0.025, 0.0125]
        self.biome_options = ["arctic", "desert", "grassland", "woodland", "tundra"]
        self.amount = {
            "wood": {
                1: random.randint(1, 2),
                2: random.randint(1, 2),
                3: random.randint(1, 2),
            }
        }

    @commands.command(name="chop")
    async def gather_start(self, ctx):
        # Gets biome from user & starting point for command
        while True:
            embed = discord.Embed(
                title="**Gathering**",
                description="**Please enter the biome you're gathering:**\n\n"
                "**Arctic**, **Desert**, **Grassland**, **Woodland**, "
                "**Tundra**",
                color=self.color,
            )
            await ctx.reply(embed=embed)

            # Check to make sure the bot is interacting with the user that called the command
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)
            self.biome = response.content.lower()
            # Checks user input against a biome_options list
            if self.biome not in self.biome_options:
                embed = discord.Embed(
                    title="**Invalid Biome**",
                    description=f"**The specified biome {self.biome} is not valid. "
                    f"Please enter a valid biome.**",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
            else:
                await self.tool_selection(ctx)
                break

    async def tool_selection(self, ctx):
        # Checks if the user is in the right location and has the proper tool to harvest wood
        while True:
            embed = discord.Embed(
                title="**Gathering**",
                description=f"**Do you have an Axe and are you near a "
                f"harvestable source of wood?**"
                f"\n\n**Yes/No**",
                color=self.color,
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
                    break
                case _:
                    embed = discord.Embed(
                        title="**Unable To Gather**",
                        description="**You can't gather wood without proper"
                        " tools or without being near a harvestable "
                        "source of wood. "
                        "Gathering ends.**",
                        color=self.color,
                    )
                    await ctx.reply(embed=embed)

    async def strength_modifier(self, ctx):
        # Gets strength or dexterity modifier from user as input
        while True:
            embed = discord.Embed(
                title="**Modifier**",
                description="**Please provide your Strength or Dexterity "
                "modifier: **",
                color=self.color,
            )
            await ctx.reply(embed=embed)

            # Check to make sure the bot is interacting with the user that called the command
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)
            self.modifier_input = response.content
            
            try:
                self.modifier_input = int(self.modifier_input)
                break
            except ValueError:
                embed = discord.Embed(
                    title="**Invalid Input**",
                    description="**Invalid input. Please provide a valid integer.**",
                    color=self.color,
                )
                await ctx.reply(embed=embed)

        await self.result(ctx)

    async def result(self, ctx):
        # Displays the results for the gathering attempt and displays the results
        num_gathered = 0
        success_count = 0
        # Loops through a success_chance list and multiplies it by the modifier provided
        for tier, success_chance in enumerate(self.success_tiers, start=1):
            modified_chance = success_chance * self.modifier_input

            if random.random() <= modified_chance:
                success_count += 1
                num_gathered += self.amount[self.material][tier]

        # If gathering is successful, displays the amount of material gained for wood
        if num_gathered > 0:
            self.file_success()
            select_response = random.choice(self.wood_response)
            embed = discord.Embed(title="**Gathering Success**", color=self.color)
            embed.add_field(
                name="**Result**", value=f"*{select_response}*", inline=False
            )
            embed.add_field(name="**Time Taken**", value="*2hrs.*", inline=False)
            embed.add_field(
                name="**Note:**",
                value=f"\n{num_gathered}x {self.material} gathered\n\n*Please contact"
                f" your DM to add the resource amounts listed.*",
            )

            await ctx.reply(embed=embed)

        else:
            self.file_failure()
            select_response = random.choice(self.f_wood_response)
            embed = discord.Embed(title="**Gathering Failed**", color=self.color)
            embed.add_field(
                name="**Result**", value=f"*{select_response}*", inline=False
            )
            await ctx.reply(embed=embed)

    def file_success(self):
        # Reads wood success response file depending on the biome selected
        with open(
            f"gather_txt/{self.biome}_wood_response.txt", encoding="utf-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.wood_response.append(response)

    def file_failure(self):
        # Reads wood failure response file depending on the biome selected
        with open(
            f"gather_txt/f_{self.biome}_wood_response.txt", encoding="utf-8"
        ) as file:
            for line in file:
                response = "".join(line.split("\n"))
                self.f_wood_response.append(response)
