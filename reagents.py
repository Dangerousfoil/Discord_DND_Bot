import discord
from discord.ext import commands


class Reagent(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.biome = ""
        self.biome_options = ["creature", "tundra", "glacier", "desert", "grasslands",
                              "forest", "fungi plains", "glowing fungi forest",
                              "glowing lichen gardens", "misting fogs", "stone valley",
                              "city sewers"]

    @commands.command(name="reagent")
    async def reagent(self, ctx):
        # Asking user location of Harvesting
        embed = discord.Embed(title='**Where are you harvesting?**',
                              description='**Options:**\n\n'
                                          '**Creature**\n'
                                          '**Tundra**'
                                          '**Glacier**'
                                          '**Desert**'
                                          '**Grasslands**'
                                          '**Forest**'
                                          '**Fungi Plains**'
                                          "**Glowing Fungi Forest**\n"
                                          "**Glowing Lichen Gardens**\n"
                                          "**Misting Fogs**\n"
                                          "**Stone Valley**\n"
                                          "**City Sewers**\n",
                              color=discord.Color.blue()
                              )
        await ctx.reply(embed=embed)

        def check_biome(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for('message', check=check_biome)
        self.biome = response.content.lower()
        if self.biome not in self.biome_options:
            embed = discord.Embed(title="**Invalid Biome**",
                                  description=f"**{self.biome.title()} is not a valid biome. " 
                                  f"Please enter a valid biome.**",
                                  color=discord.Color.red())
            await ctx.reply(embed=embed)
            await self.reagent(ctx)
        else:
            pass    
