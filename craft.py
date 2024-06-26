import discord
import math
from discord.ext import commands
from tinydb import TinyDB, Query

crafting_database = TinyDB("assets/databases/crafting_database.json")
crafting_database.default_table_name = "Crafting_Database"
recipe_database = TinyDB("assets/databases/recipe_database.json")
recipe_database.default_table_name = "Recipe_Database"
query = Query()


class Crafting(commands.Cog):
    """
    Asks user for the item and rarity they want to craft, pulls required materials
    for that item from the database and displays the information to the user.
    """

    def __init__(self, bot):
        # Declares variables for use in the class
        self.client = bot
        self.item_to_craft = ""
        self.rarity = ""
        self.rarity_options = ["Common", "Uncommon", "Rare", "Very Rare"]

    @commands.command(name="craft")
    async def run(self, ctx):
        # Gets item to be crafted from user and start of function
        embed = discord.Embed(
            title="**Item Crafting**",
            description="**What item would you like to craft?**",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interaction with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.item_to_craft = response.content.title()

        item_check = crafting_database.search(query.Name == self.item_to_craft)
        if len(item_check) == 0:
            embed = discord.Embed(
                title="**Invalid Item**",
                description="**The item you have entered is not available for crafting.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.run(ctx)
        else:
            await self.rarity_check(ctx)

    async def rarity_check(self, ctx):
        embed = discord.Embed(
            title=f"**{self.item_to_craft} Crafting**",
            description=f"**What tier would you like to craft?**",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="**Options:**", value="**`- Common\n- Uncommon\n- Rare\n- Very Rare`**"
        )
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interaction with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.rarity = response.content.title()

        if self.rarity not in self.rarity_options:
            embed = discord.Embed(
                title="**Invalid Input**",
                description="**Invalid tier selected, please choose an option from the list.**",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.rarity_check(ctx)
        else:
            self.item_information()
            self.base_materials()
            self.materials_after_rarity()
            await self.result(ctx)

    async def result(self, ctx):
        # Pools all information gathered about the item and displays it to the user
        x = self.materials_after_rarity()
        embed = discord.Embed(
            title=f"**{self.item_to_craft.title()} Crafting**",
            description="**Here is the required materials to craft your item.**",
            color=discord.Color.blue(),
        )
        embed.add_field(name="**Metal:**", value=f"*{x[0]} Pieces*", inline=True)
        embed.add_field(name="**Wood:**", value=f"*{x[1]} Pieces*", inline=True)
        embed.add_field(name="**Hide:**", value=f"*{x[2]} Pieces*", inline=True)
        embed.add_field(
            name="**Special Metals:**",
            value=f"*{x[4]} x {self.rarity.title()}*",
            inline=False,
        )
        embed.add_field(name="**Tools:**", value=f"*{x[3]}*", inline=False)
        embed.add_field(name="*Do you have the required materials?*", value="")
        await ctx.reply(embed=embed)

        # Check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        confirmation = response.content.lower()

        x = self.dc_cp_calculations()

        match confirmation:
            case "yes":
                embed = discord.Embed(
                    title=f"**Crafted {self.item_to_craft.title()}**",
                    description=f"**You have successfully crafted a {self.item_to_craft}.**\n\n"
                    f"**DC: ** *{x[1]}*\n**CP: ** *{x[0]}*",
                    color=discord.Color.blue(),
                )
                embed.set_footer(text="Please be sure to inform your DM of your crafting success")
                await ctx.reply(embed=embed)
            case "no":
                embed = discord.Embed(
                    title="**Crafting Failed**",
                    description="**You can't craft without proper materials and tools**",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)

            case _:
                embed = discord.Embed(
                    title="**Invalid Input**",
                    description="**Invalid input. Please enter a valid option.**",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                await self.result(ctx)

    def item_information(self):
        # Grabs item information from the crafting database
        x = crafting_database.search(query.Name == self.item_to_craft)
        item_class = x[0]["Class_Type"]
        item_weight = x[0]["Weight"]
        return item_weight, item_class

    def base_materials(self):
        # Grabs the correct number of materials needed to craft the item from the database
        info = self.item_information()
        recipe = recipe_database.search(query.Name == info[1])
        metal_needed = math.ceil(info[0] * recipe[0]["metal"])
        hide_needed = math.ceil(info[0] * recipe[0]["hide"])
        wood_needed = math.ceil(info[0] * recipe[0]["wood"])
        tools = recipe[0]["tools"]

        return metal_needed, hide_needed, wood_needed, tools

    def materials_after_rarity(self):
        # Combines the materials with materials with the rarity to get the special materials
        recipe = recipe_database.search(query.Name == self.rarity)
        materials = self.base_materials()
        special_metal = math.ceil(materials[0] * recipe[0]["Material"])
        total_metal = materials[0]
        total_wood = materials[2]
        total_hide = materials[1]
        tools = materials[3]
        return total_metal, total_wood, total_hide, tools, special_metal

    def dc_cp_calculations(self):
        # Gets the DC and CP for the item and does the calculations for rarity
        recipe = recipe_database.search(query.Name == self.rarity)
        print(recipe)
        item_info = crafting_database.search(query.Name == self.item_to_craft)
        print(item_info)
        item_dc = item_info[0]["DC"]
        item_cp = item_info[0]["CP"]

        rarity_dc = recipe[0]["DC"]
        rarity_cp = recipe[0]["CP"]

        crafted_item_dc = item_dc + rarity_dc
        crafted_item_cp = item_cp * rarity_cp

        return crafted_item_cp, crafted_item_dc
