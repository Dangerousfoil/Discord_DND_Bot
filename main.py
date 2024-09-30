import discord
from api import bot_one_token
from fishing import Fishing
from mine import Mine
from hunting import Hunting
from craft import Crafting
from chop import Chop
from reagents import Reagents
from discord.ext import commands

# Setup of variables for Discord bot
COGS = ["Fishing", "Mine", "Hunting", "Crafting", "Chop", "Reagents"]
VERSION = discord.__version__
INTENTS = discord.Intents.default()
INTENTS.message_content = True
client = commands.Bot(command_prefix="!", intents=INTENTS)


@client.event
async def on_ready():
    # Handles actions when the bot first comes online
    print(f"{client.user} Online. Running Version: {VERSION}")
    for cog in COGS:
        await client.add_cog(cog(client))


if __name__ == "__main__":
    client.run(bot_one_token)
