import discord
import math
from discord.ext import commands
from tinydb import TinyDB, Query

# Sets up variables for database access
crafting_database = TinyDB('databases/crafting_database.json')
crafting_database.default_table_name = 'Crafting_Database'
user = Query()


class Crafting(commands.Cog):
    def __init__(self, bot):
        self.client = bot
        self.item_choice = ''
        self.metal = 0
        self.wood = 0
        self.hide = 0
        self.uncommon = 0
        self.rare = 0
        self.very_rare = 0
        self.tool = ''
        self.item_class = ''
        self.item_weight = 0
        self.metal_weapon_rec = {'metal': 1, 'wood': 0.5, 'hide': 0.125,
                                 'tools': "Woodcarver's Tools and Smith's Tool's"}
        self.metal_armor_rec = {'metal': 1, 'wood': 0, 'hide': 0.125,
                                'tools': "Woodcarver's Tools and Smith's Tool's"}
        self.wood_weapon_rec = {'metal': 0.5, 'wood': 1, 'hide': 0.125,
                                'tools': "Woodcarver's Tools"}
        self.hide_armor_rec = {'metal': 0.125, 'wood': 0, 'hide': 1,
                               'tools': "Woodcarver's Tools and Smith's Tool's"}
        self.metal_ammo_rec = {'metal': 1, 'wood': 0, 'hide': 0,
                               'tools': "Smith's Tool's"}
        self.wood_ammo_rec = {'metal': 1, 'wood': 1, 'hide': 1,
                              'tools': "Woodcarver's Tools and Smith's Tool's"}
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

        x = crafting_database.all()
        if self.item_choice in x[0]['Name']:
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
        if self.item_class == 'Metal Weapon':
            self.metal = self.metal_weapon_rec.get('metal')
            self.wood = self.metal_weapon_rec.get('wood')
            self.hide = self.metal_weapon_rec.get('hide')
            self.tool = self.metal_weapon_rec.get('tools')
        elif self.item_class == 'Wood Weapon':
            self.metal = self.wood_weapon_rec.get('metal')
            self.wood = self.wood_weapon_rec.get('wood')
            self.hide = self.wood_weapon_rec.get('hide')
            self.tool = self.wood_weapon_rec.get('tools')
        elif self.item_class == 'Metal Armor':
            self.metal = self.metal_armor_rec.get('metal')
            self.wood = self.metal_armor_rec.get('wood')
            self.hide = self.metal_armor_rec.get('hide')
            self.tool = self.metal_armor_rec.get('tools')
        elif self.item_class == 'Hide Armor':
            self.metal = self.hide_armor_rec.get('metal')
            self.wood = self.hide_armor_rec.get('wood')
            self.hide = self.hide_armor_rec.get('hide')
            self.tool = self.hide_armor_rec.get('tools')
        elif self.item_class == 'Wood Ammo':
            self.metal = self.wood_ammo_rec.get('metal')
            self.wood = self.wood_ammo_rec.get('wood')
            self.hide = self.wood_ammo_rec.get('hide')
            self.tool = self.wood_ammo_rec.get('tools')
        elif self.item_class == 'Metal Ammo':
            self.metal = self.metal_ammo_rec.get('metal')
            self.wood = self.metal_ammo_rec.get('wood')
            self.hide = self.metal_ammo_rec.get('hide')
            self.tool = self.metal_ammo_rec.get('tools')

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
