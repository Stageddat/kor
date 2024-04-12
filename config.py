import os

import discord
import dotenv
from discord.ext import commands

bot = discord.Bot()
intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.guild_messages = True
bot = commands.Bot(command_prefix="a!", intents=intents)

admins = [756509638169460837]

# Server ID
guild_id = 1151612424785494116

# Github token
dotenv.load_dotenv()
github_token = str(os.getenv("GITHUB_TOKEN"))