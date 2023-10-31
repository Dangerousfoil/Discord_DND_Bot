import discord
from icecream import ic
from discord.ext import commands
from tinydb import TinyDB, Query

recipe_database = TinyDB("assets/databases/recipe_database.json")
recipe_database.default_table_name = "Recipe_Database"
reagent_database = TinyDB("assets/databases/reagent_database.json")
reagent_database.default_table_name = "Reagent_Database"
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
        self.effects = []
        self.level, self.modifier = 0, 0
        self.choice, self.item_strength, self.kit_choice = "", "", ""
        self.potion_strength_options = [
            "draught",
            "infusion",
            "brew",
            "concoction",
            "essence",
            "distillate",
        ]
        self.poison_strength_options = ["trace", "dab", "drop", "dose", "draft", "concentrate"]
        self.kit_options = [
            "alchemist's supplies",
            "poisner's kit",
            "brewer's supplies",
            "herbalism kit",
        ]

    @staticmethod
    def set_database(level, choice):
        
        return recipe_db

    @staticmethod
    def check_ingredients(name):
        ingredient_db = reagent_database.all()

        if name not in ingredient_db[0]["Name"]:
            embed = discord.Embed(
                title="Invalid Input",
                description=f"{name.title()} is not a recognized ingredient.",
                color=discord.Color.red(),
            )
        else:
        
            return embed, name

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
            if self.level != 20:
                if self.level in range(1, 3):
                    self.level = 3
                elif self.level in range(5, 7):
                    self.level = 7
                elif self.level in range(8, 11):
                    self.level = 11
                elif self.level in range(12, 15):
                    self.level = 15
                elif self.level in range(16, 19):
                    self.level = 19
            else:
                self.level = 20
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

    async def item_strength_check(self, ctx):
        match self.choice:
            case "potion":
                embed = discord.Embed(
                    title="Brewing",
                    description="Please select the strength of the item you want to craft:\n"
                    "-Draught\n-Infusion\n-Brew\n-Concoction\n-Essence\n-Distillate",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)
            case "poison":
                embed = discord.Embed(
                    title="Brewing",
                    description="Please select the strength of the item you want to craft:\n"
                    "-Trace\n-Dab\n-Drop\n-Dose\n-Draft\n-Concentrate",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        self.item_strength = response.content.lower()

        if self.item_strength not in self.poison_strength_options or self.potion_strength_options:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please select a strength from the options provided.",
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)
        else:
            await self.brew_effects(ctx)

    async def brew_effects(self, ctx):
        db_check = reagent_database.all()
        raw_effect_data = []

        embed = discord.Embed(
            title="Brewing",
            description="How many ingredients do you want to add?",
            color=discord.Color.blue()
        )
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        response = await self.client.wait_for("message", check=check)

        try:
            number_of_ingredients = int(response.content)
        except ValueError:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please enter a valid integer for the amount of ingredients you wish to add.",
                color=discord.Color.red()
            )
            await ctx.reply(embed=embed)
            await self.brew_effects(ctx)
        
        i = 0
        while i != number_of_ingredients:
            embed = discord.Embed(
                title="Brewing",
                description="Enter an ingredient to add to your brew",
                color=discord.Color.blue()
            )
            await ctx.reply(embed=embed)

            response = await self.client.wait_for("messsage", check=check)
            ingredient = response.content.title()

            if ingredient not in db_check[0]["Name"]:
                embed = discord.Embed(
                    title="Invalid Input",
                    description=f"{ingredient} is not a supported ingredient",
                    color=discord.Color.red()
                )
                await ctx.reply(embed=embed)
            else:
                ingredient_db = reagent_database.search(query.Name == ingredient)         
            
            for item in ingredient_db[0]["Effect"]:
                raw_effect_data.append(item)
            i += 1

        for item in raw_effect_data:
            if raw_effect_data.count(item) >= 2:
                if item in self.effects:
                    raw_effect_data.remove(item)
                else:
                    self.effects.append(item)
        
        
    async def results(self, ctx):
        pass
