import discord
import math
from discord.ext import commands
from tinydb import TinyDB, Query

crafting_database = TinyDB("databases/crafting_database.json")
crafting_database.default_table_name = "Crafting_Database"
recipe_database = TinyDB("databases/recipe_database.json")
recipe_database.default_table_name = "Recipe_Database"
query = Query()


class Crafting(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.item_to_craft = ""
        self.rarity = ""
        self.rarity_options = ["common", "uncommon", "rare", "very rare"]

    @commands.command(name="craft")
    async def run(self, ctx):
        embed = discord.Embed(
            title="Item Crafting",
            description="What item would you like to craft?",
            color=discord.Color.blue(),
        )
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.item_to_craft = response.content.title()

        item_check = crafting_database.search(query.Name == self.item_to_craft)
        if len(item_check) == 0:
            embed = discord.Embed(
                title="Invalid Item",
                description="The item you have entered is not avaiable for crafting.",
                color=discord.Color.red(),
            )
            await ctx.reply(embed=embed)
            await self.run(ctx)
        await self.rarity_check(ctx)

    async def rarity_check(self, ctx):
        embed = discord.Embed(
            title=f"{self.item_to_craft} Crafting",
            description=f"What tier would you like to craft?",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Options:", value="-Common\n-Uncommon\n-Rare\n-Very Rare")
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        self.rarity = response.content.lower()

        if self.rarity not in self.rarity_options:
            embed = discord.Embed(
                title="Invalid Input",
                description="Invalid tier selected please chose an option from the list.",
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
        x = self.materials_after_rarity()
        embed = discord.Embed(
            title=f"{self.item_to_craft.title()} Crafting",
            description="Here is the required materials to craft your item.",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Metal:", value=f"{x[0]}", inline=False)
        embed.add_field(name="Wood:", value=f"{x[1]}", inline=False)
        embed.add_field(name="Hide:", value=f"{x[2]}", inline=False)
        embed.add_field(name="Tools:", value=f"{x[3]}", inline=False)
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for("message", check=check)
        confirmation = response.content.lower()

        match confirmation:
            case "yes":
                embed = discord.Embed(
                    title=f"{self.item_to_craft.title()} Crafting",
                    description=f"You have successfully crafted a {self.item_to_craft}!",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)
            case "no":
                embed = discord.Embed(
                    title="Crafting Failed",
                    description="You can't craft without proper materials and tools",
                    color=discord.Color.blue(),
                )
                await ctx.reply(embed=embed)
            case _:
                await self.result(ctx)

    def item_information(self):
        x = crafting_database.search(query.Name == self.item_to_craft)
        item_class = x[0]["Class_Type"]
        item_weight = x[0]["Weight"]
        return item_weight, item_class

    def base_materials(self):
        info = self.item_information()
        recipe = recipe_database.search(query.Name == info[1])
        metal_needed = math.ceil(info[0] * recipe[0]["metal"])
        hide_needed = math.ceil(info[0] * recipe[0]["hide"])
        wood_needed = math.ceil(info[0] * recipe[0]["wood"])
        tools = recipe[0]["tools"]

        return metal_needed, hide_needed, wood_needed, tools

    def materials_after_rarity(self):
        recipe = recipe_database.search(query.Name == self.rarity)
        materials = self.base_materials()
        total_metal = math.ceil(materials[0] * recipe[0]["Material"] + materials[0])
        total_hide = math.ceil(materials[1] * recipe[0]["Material"] + materials[1])
        total_wood = math.ceil(materials[2] * recipe[0]["Material"] + materials[2])
        tools = materials[3]
        return total_metal, total_wood, total_hide, tools
