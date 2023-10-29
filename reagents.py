import discord
from discord.ext import commands


class Reagent(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        pass

    @commands.command(name="reagent")
    async def reagent(self, ctx):
        # Asking user location of Harvesting
        embed = discord.Embed(title='**Where are you harvesting?**',
                              description='**Options:**\n\n'
                                          '**`Creature`**\n'
                                          '**`Tundra`**'
                                          '**`Glacier`**'
                                          '**`Desert`**'
                                          '**`Grasslands`**'
                                          '**`Forest`**'
                                          '**`Fungi Plains`**'
                                          "**`Glowing Fungi Forest`**\n"
                                          "**`Glowing Lichen Gardens`**\n"
                                          "**`Misting Fogs`**\n"
                                          "**`Stone Valley`**\n"
                                          "**`City Sewers`**\n",
                              color=discord.Color.blue()
                              )
        await ctx.reply(embed=embed)

        def check_biome(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for('message', check=check_biome)
        biomes = response.content.lower()
