import discord
import random
from discord.ext import commands
from tinydb import TinyDB, Query

reagent_database = TinyDB("assets/databases/reagent_database.json")
reagent_database.default_table_name = "Reagent_Database"
user = Query()


class Reagents(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.biome = ""
        self.herbalism_modifier = 0
        self.proficiency_bonus = 0
        self.proficiency = False
        self.biome_options = [
            "creature",
            "tundra",
            "glacier",
            "desert",
            "grasslands",
            "forest",
            "fungi plains",
            "glowing fungi forest",
            "glowing lichen gardens",
            "misting fogs",
            "stone valley",
            "city sewers",
        ]

        @commands.command(name="reagent")
        async def reagent(self, ctx):
            # Ask user location of harvest
            embed = discord.Embed(
                title="**Where are you harvesting?**",
                description="**Options:**\n\n**Creature**\n**Tundra**\n**Glacier**\n**Desert**\n**Grasslands**\n**Forest**\n**Fungi Plains**\n**Glowing Fungi Forest**\n**Glowing Lichen Gardens**\n**Misting Fogs**\n**Stone Valley**\n**City Sewers**\n",
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)

            # Check to make sure the bot is interacting with the user that called the command
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)

            self.biome = response.content.lower()

            if self.biome not in self.biome_options:
                embed = discord.Embed(
                    title="**Invalid Biome**",
                    description=f"**{self.biome.title()} is not a vaild biome. Please enter a valid biome.",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                await self.reagent(ctx)
            else:
                await self.modifier(ctx)

        async def modifier(self, ctx):
            embed = discord.Embed(
                title="**Nature/Survival Modifier**",
                description="*Please enter your **Nature/Survival** modifier.*\n",
                color=discord.Color.green(),
            )
            await ctx.reply(embed=embed)

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            response = await self.client.wait_for("message", check=check)

            try:
                self.herbalism_modifier = int(response.content)
            except ValueError:
                embed = discord.Embed(
                    title="**Invalid Input**",
                    description=f"**A number must be entered.**",
                    color=discord.Color.red(),
                )
                await ctx.reply(embed=embed)
                await self.modifier(ctx)

            embed = discord.Embed(
                title="**Herbalism Kit Proficiency**",
                description="*Do you have an **`Herbalism kit`** and are proficient with it?*\n"
                "Yes/No",
                color=discord.Color.blue(),
            )
            await ctx.reply(embed=embed)

            response = await self.client.wait_for("message", check=check)

            match response.content.lower():
                case "yes":
                    self.proficiency = True
                case "no":
                    self.proficiency = False
                case _:
                    embed = discord.Embed(
                        title="**Invalid Input**",
                        description=f"**Expected [Yes] or [No]. Got {response.content}",
                        color=discord.Color.red(),
                    )
            await ctx.reply(embed=embed)

            embed = discord.Embed(
                title="**Proficiency Bonus**",
                description="*Please enter your **`Proficiency Bonus`** *\n",
                color=discord.Color.green(),
            )
            await ctx.reply(embed=embed)

            response = await self.client.wait_for("message", check=check)

            try:
                self.proficiency_bonus = int(response.content)
            except ValueError:
                embed = discord.Embed(
                    title="**Invalid Input**",
                    description=f"**A number must be entered.**",
                    color=discord.Color.red(),
                )
            await ctx.reply(embed=embed)
            await self.result(ctx)

        async def result(self, ctx):
            herbs = reagent_database.search(user.Biome == self.biome)

            if self.herbalism_modifier >= 6:
                accessible_tiers = ["Common", "Uncommon", "Rare"]
            elif self.herbalism_modifier >= 3:
                accessible_tiers = ["Common", "Uncommon"]
            else:
                accessible_tiers = ["Common"]

            filtered_herbs = [h for h in herbs if h["Tier"] in accessible_tiers]

            herb = random.choice(filtered_herbs)
            herb_name = herb.get("Name")
            herb_rarity = herb.get("Tier")

            if self.proficiency:
                self.total_collected = self.proficiency_bonus
            else:
                self.total_collected = 1

            embed = discord.Embed(
                title="Reagent Found and Total Collected", color=discord.Color.blue()
            )
            embed.add_field(name="Name", value=f"**{herb_name}**")
            embed.add_field(name="Rarity", value=f"**{herb_rarity}**")
            embed.add_field(name="Total Collected", value=f"**{self.total_collected}**")

            await ctx.reply(embed=embed)
