import discord
from api import bot_one_token
from fishing import Fishing
from mine import Mine
from hunting import Hunting
from craft import Crafting
from chop import Chop
from reagents import Reagent
from discord.ext import commands

# Setup of variables for Discord bot
version = discord.__version__
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)


@client.event
async def on_ready():
    # Handles actions when the bot first comes online
    print(f"{client.user} Online. Running Version: {version}")
    await client.add_cog(Fishing(client))
    await client.add_cog(Mine(client))
    await client.add_cog(Hunting(client))
    await client.add_cog(Crafting(client))
    await client.add_cog(Chop(client))
    await client.add_cog(Reagent(client))


if __name__ == "__main__":
    client.run(bot_one_token)
