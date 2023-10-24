import discord
from api import bot_one_token
from gathering import Gathering
from fishing import Fishing
from mine import Mine
from hunting import Hunting
from crafting import Crafting
from chop import Chop
from discord.ext import commands

version = discord.__version__
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print(f'{client.user} Online. Running Version: {version}')
    await client.add_cog(Gathering(client))
    await client.add_cog(Fishing(client))
    await client.add_cog(Mine(client))
    await client.add_cog(Hunting(client))
    await client.add_cog(Crafting(client))
    await client.add_cog(Chop(client))


client.run(bot_one_token)
