import discord
import random
from discord.ext import commands


class Gathering(commands.Cog):
    """
    Simulates gathering wood and metal in different biomes. Using a percent chance to determine
    the amount of materials harvested per cycle. Gives players flavor text for successful attempts
    and for failed attempts.
    """

    def __init__(self, bot):
        # Declares variables/lists/dictionaries for use in the class
        self.client = bot
        self.biome = None
        self.material = None
        self.modifier_input = 0
        self.color = discord.Color.blue()
        self.metal_image = discord.File('images/materials/metal.png',
                                        filename='metal.png')
        self.wood_image = discord.File('images/materials/wood.png', filename='wood.png')
        self.wood_response = []
        self.metal_response = []
        self.f_wood_response = []
        self.f_metal_response = []
        self.success_tiers = [1.0, 0.10, 0.05]
        self.gather_options = ['wood', 'metal']
        self.tool_options = {'metal': 'a pickaxe', 'wood': 'an axe'}
        self.biome_options = ['arctic', 'desert', 'grassland', 'woodland', 'tundra']
        self.amount = {'wood': {1: random.randint(2, 2), 2: random.randint(1, 1),
                                3: random.randint(1, 1)}, 'metal': {1: 1, 2: 1, 3: 1}}

    @commands.command(name='gather')
    async def gather_start(self, ctx):
        # Gets biome from user & starting point for command
        embed = discord.Embed(title='**Gathering**',
                              description="**Please enter the biome you're gathering in:**\n\n"
                                          "**Arctic**, **Desert**, **Grassland**,**Woodland**, "
                                          "**Tundra**", color=self.color)
        await ctx.reply(embed=embed)

        # Performs check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for('message', check=check)
        self.biome = response.content.lower()
        # Checks user input against biome_options list
        if self.biome not in self.biome_options:
            embed = discord.Embed(title='**Invalid Biome**',
                                  description=f'**The specified biome {self.biome} is not valid. '
                                              f'Please enter a valid biome.**',
                                  color=discord.Color.red())
            await ctx.reply(embed=embed)
        else:
            await self.material_selection(ctx)

    async def material_selection(self, ctx):
        # Gets material to be harvested from user
        embed = discord.Embed(title='**Gathering**',
                              description='**What are you trying to gather?**', color=self.color)
        embed.add_field(name='**Options:**', value='**Wood, Metal**', inline=False)
        await ctx.reply(embed=embed)

        # Performs check to make sure the bot is interacting with the user that called the command
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.client.wait_for('message', check=check)
        material_input = response.content.lower()
        # Checks user input against gather_options list
        if material_input in self.gather_options:
            self.material = material_input
        else:
            embed = discord.Embed(title='**Invalid Material**',
                                  description=f'**The specified material {material_input} is not '
                                              f'valid. Please enter a valid material.**',
                                  color=self.color)
            await ctx.reply(embed=embed)
        await self.tool_selection(ctx)

    async def tool_selection(self, ctx):
        # Checks if user has proper tool to harvest the requested material
        embed = discord.Embed(title='**Gathering**',
                              description=f'**Do you have {self.tool_options[self.material]} for '
                                          f'gathering {self.material}?**\n\n**Yes/No**',
                              color=self.color)
        await ctx.reply(embed=embed)
        response = await self.client.wait_for('message')
        tool_input = response.content.lower()
        # Tells user they are unable to harvest materials if they do not have the proper tool
        if tool_input != 'yes':
            embed = discord.Embed(title='**Unable To Gather**',
                                  description="You can't gather anything without proper tools. "
                                              "Gathering ends.**",
                                  color=self.color)
            await ctx.reply(embed=embed)
        await self.strength_modifier(ctx)

    async def strength_modifier(self, ctx):
        # Gets strength or dexterity modifier from user as input
        embed = discord.Embed(title='**Modifier**',
                              description='**Please provide your Strength or Dexterity '
                                          'modifier: **', color=self.color)
        await ctx.reply(embed=embed)
        response = await self.client.wait_for('message')
        self.modifier_input = response.content
        # Checks to make sure the user has entered a number and displays an invalid input if False
        try:
            self.modifier_input = int(self.modifier_input)
        except ValueError:
            embed = discord.Embed(title='**Invalid Input**',
                                  description='**Invalid input. Please provide a valid integer.**',
                                  color=self.color)
            await ctx.reply(embed=embed)
        await self.location(ctx)

    async def location(self, ctx):
        # Asks the user if they are near a source of the requested material
        embed = discord.Embed(title='**Gathering**',
                              description=f'**Are you near a harvestable source of {self.material}'
                                          f'?**\n\n**Yes/No**',
                              color=self.color)
        await ctx.reply(embed=embed)
        response = await self.client.wait_for('message')
        location_input = response.content.lower()
        # If the user is not near a source of the requested material end gathering
        if location_input != 'yes':
            embed = discord.Embed(title='**Unable To Gather**',
                                  description='**You are not in the right location to gather '
                                              'resources. Gathering ends**.',
                                  color=self.color)
            await ctx.reply(embed=embed)
        await self.result(ctx)

    async def result(self, ctx):
        # Displays the results for the gathering attempt and displays the results
        num_gathered = 0
        success_count = 0
        # Loops through success_chance list and multiplies it by the modifier provided
        for tier, success_chance in enumerate(self.success_tiers, start=1):
            modified_chance = success_chance * self.modifier_input

            if random.random() <= modified_chance:
                if self.material == 'wood':
                    success_count += 1
                    num_gathered += self.amount[self.material][tier]
                elif self.material == 'metal':

                    success_count += 1
                    num_gathered += self.amount[self.material][tier]
        # If gathering is successful displays the amount of materials gained for wood
        if num_gathered > 0 and self.material == 'wood':
            # Calls method that handles getting the responses for failures
            self.file_success()
            select_response = random.choice(self.wood_response)
            embed = discord.Embed(title='**Gathering Success**', color=self.color)
            embed.add_field(name='**Result**', value=f'*{select_response}*', inline=False)
            embed.add_field(name='**Time Taken**', value='*2hrs.*', inline=False)
            embed.add_field(name='**Note:**',
                            value=f'\n{num_gathered}x {self.material} gathered\n\n*Please contact'
                                  f' your DM to add the resource amounts listed.*')
            embed.set_thumbnail(url='attachment://wood.png')
            await ctx.reply(file=self.wood_image, embed=embed)
        # If gathering is successful displays the amount of materials gained for metal
        elif num_gathered > 0 and self.material == 'metal':
            # Calls method that handles getting the responses for failures
            self.file_success()
            select_response = random.choice(self.metal_response)
            embed = discord.Embed(title='**Gathering Success**', color=self.color)
            embed.add_field(name='**Result:**', value=f'*{select_response}*', inline=False)
            embed.add_field(name='**Time Taken:**', value='*2hrs.*', inline=False)
            embed.add_field(name='**Note:**',
                            value=f'*{num_gathered}x {self.material} gathered\n\n\nPlease contact*'
                                  f' *your DM to add the resource amounts listed.*')
            embed.set_thumbnail(url='attachment://metal.png')
            await ctx.reply(file=self.metal_image, embed=embed)
        else:
            # If gathering is failed displays failure response
            if self.material == 'wood':
                # Calls method that handles getting the responses for failures
                self.file_failure()
                select_response = random.choice(self.f_wood_response)
                embed = discord.Embed(title='**Gathering Failed**', color=self.color)
                embed.add_field(name='**Result**', value=f'*{select_response}*', inline=False)
                await ctx.reply(embed=embed)
            elif self.material == 'metal':
                # Calls method that handles getting the responses for failures
                self.file_failure()
                select_response = random.choice(self.f_metal_response)
                embed = discord.Embed(title='**Gathering Failed**', color=self.color)
                embed.add_field(name='**Result**', value=f'*{select_response}*', inline=False)
                await ctx.reply(embed=embed)

    def file_success(self):
        # Reads wood success response file depending on the biome selected
        with open(f'gather_txt/{self.biome}_wood_response.txt', encoding='utf-8') as file:
            for line in file:
                response = ''.join(line.split('\n'))
                self.wood_response.append(response)
        # Reads metal success response file depending on the biome selected
        with open(f'gather_txt/{self.biome}_metal_response.txt', encoding='utf-8') as file:
            for line in file:
                response = ''.join(line.split('\n'))
                self.metal_response.append(response)

    def file_failure(self):
        # Reads metal failure response file depending on the biome selected
        with open(f'gather_txt/f_{self.biome}_metal_response.txt', encoding='utf-8') as file:
            for line in file:
                response = ''.join(line.split('\n'))
                self.f_metal_response.append(response)
        # Reads wood failure response file depending on the biome selected
        with open(f'gather_txt/f_{self.biome}_wood_response.txt', encoding='utf-8') as file:
            for line in file:
                response = ''.join(line.split('\n'))
                self.f_wood_response.append(response)
