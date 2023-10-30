import discord
from discord.ext import commands
from tinydb import TinyDB, Query

recipe_database = TinyDB("assets/databases/recipe_database.json")
recipe_database.default_table_name = "Recipe_Database"
query = Query()


class Brew(commands.Cog):
    """
    Gets the level and kit type of the user for brewing potions or poison. The user level will
    decide what level of potion/poison the user will be able to create. Potion/Poison creation
    will be based on what ingedients the user has. Matching ingedient effects will be combined
    into the final effect the potion/poison will have.
    """

    def __init__(self, bot):
        # Delares variables/lists/dictionaries for use in class
        self.client = bot
        self.kit_options = [
            "alchemist's supplies",
            "poisner's kit",
            "brewer's supplies",
            "herbalism kit",
        ]
        self.level, self.modifier, self.kit_choice = 0, 0, ""

    @commands.command(name="brew")
    async def run(self, ctx):
        # Gets kit from user and starting point for command
        embed = discord.Embed(
            title="**Brewing**",
            description="**Please select the kit you're using:**\n**Options:**\n"
            "-Alchemist's Supplies\n-Poisner's Kit\n-Brewer's Supplies\n-Herbalism Kit",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        if response.content.lower() not in self.kit_options:
            embed = discord.Embed(
                title="**Invalid Input**",
                description="**Invalid Input. Please pick a kit from the list provided.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.run(ctx)
        else:
            self.kit_choice = response.content
            await self.proficiency_modifier(ctx)

    async def proficiency_modifier(self, ctx):
        # Gets user proficiency modifier and checks it is an integer
        embed = discord.Embed(
            title="**Brewing**",
            description="**Please enter your Proficiency Modifier**",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        try:
            self.modifier = int(response.content)
            await self.level_check(ctx)
        except ValueError:
            embed = discord.Embed(
                title="**Invalid Input**",
                description="**Please input a valid integer for your proficiency modifier.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.proficiency_modifier(ctx)

    async def level_check(self, ctx):
        # Gets level from user and checks to make sure it is an integer
        embed = discord.Embed(
            title="**Brewing**",
            description="**Please enter your character level.",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        try:
            self.level = int(response.content)
            await self.item_check(ctx)

        except ValueError:
            embed = discord.Embed(
                title="**Invalid Input**",
                description="**Please input a valid integer for your level.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.level_check(ctx)

    async def item_check(self, ctx):
        # Asks the user what they are brewing
        embed = discord.Embed(
            title="**Brewing**",
            description="**Are you trying to brew a potion or poison.**",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the suer that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        if response.content.lower() != "potion" or response.content.lower() != "poison":
            embed = discord.Embed(
                title="**Invalid Input**",
                description="***Invalid input please choice from the list provided**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)

        
