import discord
import math
from discord.ext import commands
from tinydb import TinyDB, Query

# Sets up variables for database access
crafting_database = TinyDB('databases/crafting_database.json')
recipe_database = TinyDB('databases/recipe_database.json')
user = Query()


class Crafting(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.item_choice, self.tool, self.item_class = '', '', ''
        self.metal, self.wood, self.hide, self.item_weight = 0, 0 , 0, 0

        self.uncommon = 0
        self.rare = 0
        self.very_rare = 0
        self.special_rec = {'uncommon': 0.1, 'rare': 0.05, 'very rare': 0.025}
        self.tier = {'uncom_dc': 1, 'uncom_cp': 2, 'rare_dc': 2, 'rare_cp': 10, 'vrare_dc': 3,
                     'vrare_cp': 100}

    @commands.command(name='craft')
    async def craft_start(self, ctx):
        embed = discord.Embed(title='**Crafting**',
                              description=f'**Please enter the item you wish to craft.**',
                              color=discord.Color.blue())
        embed.add_field(name='', value='*You can find a list of items to craft in the inventory '
                                       'management screen of your DnD Beyond Character Sheet.*')
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        response = await self.client.wait_for('message', check=check)
        self.item_choice = response.content.title()

        db = crafting_database.all()
        print(db)
        if self.item_choice in db[0]['Name']:
            await self.craft(ctx)
        else:
            await self.craft_start(ctx)

    async def craft(self, ctx):
        x = crafting_database.search(user.Name == self.item_choice)
        if self.item_choice in x[0]['Name']:
            self.item_weight = x[0]['Weight']
            self.item_class = x[0]['Class_Type']
            await self.recipe_check(ctx)
        else:
            embed = discord.Embed(title='**Invalid Input**',
                                  description=f'*{self.item_choice} is not an approved item for '
                                              f'crafting.*',
                                  color=discord.Color.red())
            embed.add_field(name='**Additional Information:**',
                            value='*If you feel this is incorrect please contact your DM or '
                                  'an ADMIN*')
            await ctx.reply(embed=embed)
            await self.craft_start(ctx)

    async def recipe_check(self, ctx):
        x = self.item_class.replace(' ','_').lower()
        recipe = recipe_database.search(user.Name == x)
        print(recipe)

        self.metal = recipe.get('metal')
        self.wood = recipe.get('wood')
        self.hide = recipe.get('hide')
        self.tool = recipe.get('tools')
    
        await self.material_skill_check(ctx)

    async def materials_needed(self):

        metal_needed = math.ceil(self.item_weight * self.metal)
        wood_needed = math.ceil(self.item_weight * self.wood)
        hide_needed = math.ceil(self.item_weight * self.hide)

        return metal_needed, wood_needed, hide_needed

    async def material_skill_check(self, ctx):
        x = await self.materials_needed()
        embed = discord.Embed(title=f'**Crafting {self.item_choice}**',
                              description=f'**Here are the requirements for your craft**',
                              color=discord.Color.blue())
        embed.add_field(name='**Materials Required:**',
                        value=f'**Metal:**  *{x[0]}*\n**Wood:**  *{x[1]}*\n**Hide:**  *{x[2]}*\n',
                        inline=False)
        embed.add_field(name='**Tool Requirement:**',
                        value=f'*{self.tool}*\n\n**Do you have everything listed above?**',
                        inline=False)
        await ctx.reply(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for('message', check=check)
        mat_check = response.content.lower()

        match mat_check:
            case 'yes':
                embed = discord.Embed(title='**Crafting Success**',
                                      description=f'**Congratulations you successfully crafted a '
                                                  f'{self.item_choice}.**',
                                      color=discord.Color.blue())
                embed.add_field(name='',
                                value='*Please be sure to inform your DM of your crafting '
                                      'success*', inline=False)
                await ctx.reply(embed=embed)
            case 'no':
                embed = discord.Embed(title='**Crafting Failed**',
                                      description=f"**You don't have the required items to craft "
                                                  f'a {self.item_choice}.**',
                                      color=discord.Color.blue())
                await ctx.reply(embed=embed)

            case _:
                embed = discord.Embed(title='**Invalid Input**',
                                      description=f"**Invalid Input, please try again**",
                                      color=discord.Color.blue())
                await ctx.reply(embed=embed)
                await self.material_skill_check(ctx)
