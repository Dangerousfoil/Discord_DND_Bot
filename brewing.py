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
        self.proficiency, self.user_lvl = 0, 0
        self.kit, self.strength, self.brew_choice = "", "", ""
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

    # Gets user level and start of brew function
    @commands.command(name="brew")
    async def brew_start(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter your character level to start brewing",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Checks to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        try:    # Tries turning user input into an integer if not prompts invalid input
                # Sets user level to the highest for the range to get correct recipe from database
            self.user_lvl = int(response.content)
            if self.user_lvl != 20: 
                if self.user_lvl in range(1, 3):
                    self.user_lvl = 3
                elif self.user_lvl in range(5, 7):
                    self.user_lvl = 7
                elif self.user_lvl in range(8, 11):
                    self.user_lvl = 11
                elif self.user_lvl in range(12, 15):
                    self.user_lvl = 15
                elif self.user_lvl in range(16, 19):
                    self.user_lvl = 19
            else:
                self.user_lvl = 20
            await self.brew_selection(ctx)  # Starts brew selection method
            print(f"User Level Logged: {self.user_lvl}")
        except TypeError:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please provide a proper input",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.brew_start(ctx)  # Recursion for error handling

    # Gets desired item the user wants to brew i.e. potion or poison
    async def brew_selection(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter what you want to brew?\n-Potion\n-Poison",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is intereacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.choice = response.content.lower()

        # Checks user input to for proper input
        if self.choice != "potion" or self.choice != "poison":
            embed = discord.Embed(
                title="Invalid Input",
                description="Please provide a proper input",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.brew_selection(ctx)  # Recursion for error handling
        else:
            print(f"Brewing: {self.choice}")
            await self.brew_strength(ctx)  # Starts brew strength method

    # Gets desired brew strength from user
    async def brew_strength(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter the strength of your brew",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Checks to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.strength = response.content.lower()
        print(f"Brew Stength: {self.strength}")

        # Checks if player input is in either lists of options
        if self.strength not in self.poison_strength_options or self.potion_strength_options:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please enter a proper input",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.brew_strength(ctx)  # Recursion for error handling
        else:
            await self.brew_kit(ctx)  # Starts brew kit method

    # Gets kit being used by the user
    async def brew_kit(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter the kit you are using to brew",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Checks to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.kit = response.content.lower()
        print(f"Kit Selected: {self.kit}")

        # Checks if player input is in kit options
        if self.kit not in self.kit_options:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please enter a proper input",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.brew_kit(ctx)  # Recursion for error handling
        else:
            await self.brew_proficiency(ctx)  # Starts brew proficiency method

    # Gets proficiency bonus from user
    async def brew_proficiency(self, ctx):
        embed = discord.Embed(
            title="Brewing",
            description="Please enter your proficiency bonus",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Checks to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)

        try:  # Tries turning user input into an integer if not prompts invalid input
            self.proficiency = int(response.content)
            print(f"User Proficiency: {self.proficiency}")
            await self.brew_ingredients(ctx)  # Starts brew ingredients method
        except TypeError:
            embed = discord.Embed(
                title="Invalid Input",
                description="Please enter a proper input",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.brew_proficiency(ctx)  # Recursion for error handling

    # Gets ingredients from user based on the brew strength entered by user
    async def brew_ingredients(self, ctx):
        ingredient_db = reagent_database.all()
        raw_effects_data = []
        brew_recipe = recipe_database.search(query.Type == self.strength.title())
        x = brew_recipe[0]["Ingredients"]
        embed = discord.Embed(
            title="Brewing",
            description=f"{x} x ingredients are need to brew a {self.strength.lower()} {self.brew_choice}",
            color=discord.Color.blue(),
        )
        ingredient_embed = await ctx.reply(embed=embed)

        i = 0
        while i != x:
            embed = discord.Embed(
                title="Brewing",
                description="Please enter an item to add to the brew",
                color=discord.Color.blue(),
            )
            await ingredient_embed.edit(embed=embed) # Updates previous embed message with looped message

            # Checks to make sure the bot is interacting with the user that called the command
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)
            ingredient_input = response.content.title()

            if ingredient_input not in ingredient_db[0]["Name"]:
                embed = discord.Embed(
                    title="Invalid Input",
                    description="Please provide a proper input",
                    color=discord.Color.red()
                )
                await ctx.reply(embed=embed)
            else:
                x = ingredient_db[0]["Effect"]
                raw_effects_data.append(x)
            i += 1
        
        for item in raw_effects_data:
            if raw_effects_data.count(item) >= 2:
                if item in self.effects:
                    raw_effects_data.remove(item)
                else:
                    self.effects.append(item)

    async def results(self, ctx):
        effects = self.effects
        embed = discord.Embed(
            title="Brewing",
            description=f"You crafted a {self.brew_choice.title()} of {effects}"
        )
