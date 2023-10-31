import discord
from icecream import ic
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
        self.level, self.modifier = 0, 0
        self.choice, self.kit_choice = "", ""
        self.craft_options = []
        self.kit_options = [
            "alchemist's supplies",
            "poisner's kit",
            "brewer's supplies",
            "herbalism kit",
        ]

    @commands.command(name="brew")
    async def brew_check(self, ctx):
        # Gets kit from user and starting point for command
        embed = discord.Embed(
            title="**Brewing**",
            description="Would you like to brew a potion or a poison?",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        match response.content.lower():
            case "potion":
                self.choice = response.content.lower()
                await self.kit_check(ctx)
            case "poison":
                self.choice = response.content.lower()
                await self.kit_check(ctx)
            case _:
                embed = discord.Embed(
                    title="Invalid Input",
                    description="Please select either potion or poison.",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                await self.brew_check(ctx)

    async def kit_check(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please select the kit you're using",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Options",
            value="-Alchemist's Supplies\n-Poisner's Kit\n-Brewser's Supplies\n-Herbalism Kit",
        )
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        if response.content.lower() not in self.kit_options:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please select from the provided options",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.kit_check(ctx)
        else:
            self.kit_choice = response.content.lower()
            await self.level_check(ctx)

    async def level_check(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter your character level",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        try:
            self.level = int(response.content)
            await self.modifier_check(ctx)
        except ValueError:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please enter a valid integer for your level",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.level_check(ctx)


    async def modifier_check(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter your Proficiency Modifier",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        try:
            self.modifier = int(response.content)
        except ValueError:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please enter a valid integer for your modifier",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.modifier_check(ctx)

    @staticmethod
    def set_database(level, choice):
        db = recipe_database.search(query.Type == choice)
        crafting_options = [item for item in db[0]["Level"] <= level]
        return crafting_options


choice = input("what do you want to make\n>>>")
print(f"User Choice: {choice}")
level = int(input("enter your level\n>>>"))
print(f"User Level: {level}")

# if level in range(0, 3):
#     level = 1
# elif level in range(4, 7):
#     level = 2
# elif level in range(8, 11):
#     level = 3
# elif level in range(12, 15):
#     level = 4
# elif level in range(16, 19):
#     level = 5
# elif level == 20:


db = recipe_database.search((query.Type == choice.title()) & (query.Level <= level))


