from datetime import datetime

import discord
import dotenv
import pytz
from discord.ext import commands, tasks

from config import bot

from src.global_src.global_path import (
    daily_count_path,
)

import random

dotenv.load_dotenv()

class daily_summary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_ready(self):
        daily_summary_loop.start()

def setup(bot):
    bot.add_cog(daily_summary(bot))

last_sent = None


@tasks.loop(seconds=10)
async def daily_summary_loop():
    global last_sent
    now = datetime.now(pytz.utc)
    cest = pytz.timezone("Europe/Madrid")
    if now.astimezone(cest).hour == 17 and now.astimezone(cest).minute == 00:
        # print("ITS TIME FOR NEW!")
        if last_sent is None or now.date() != last_sent:
            last_sent = now.date()
            channel = bot.get_channel(1151613381745311754)
            embed = discord.Embed(
                title=f"Daily ticket summary {now.month}/{now.day}/{now.year}",
                description=f"Opened ticket: \n",
                colour=discord.Colour(int("d1e8fa", 16)),
            )

            await daily_log_channel.send(embed=embed)
    else:
        pass