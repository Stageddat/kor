import json
from src.global_src.global_path import bssUpdateCodesPath
from config import bot
import discord

def loadUpdateCodesData():
    try:
        with open(bssUpdateCodesPath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

async def sendNewCodeNotification(code):
    updateCodes = loadUpdateCodesData()
    channel = await bot.fetch_channel(updateCodes["notificationChannelID"])
    codeEmbed = discord.Embed(
        title="New BSS code!",
        description=f"```{code}```",
        colour=discord.Colour(int("6798ed", 16)),
    )
    await channel.send(content="<@&1323389335298375690>", embed=codeEmbed)