
import json
import random
import discord
from discord.ext import commands

class gamble(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name = "gamble", description = "Gamble! Why not?")
    async def gamble_callback(self, ctx: discord.ApplicationContext, amount: int):
        if amount <= 0 or amount != int(amount):
            await ctx.respond(f"<@{ctx.user.id}>\nYou have to put a positive number!") 
            return

        # Load db
        with open('db/gamble/gamble_db.json', 'r') as file:
            data = json.load(file)

        user_id = str(ctx.user.id)

        # Check if exist, if not add
        if user_id not in data:
            data[user_id] = 100
            await ctx.respond("You have successfully registered! Your initial balance is $100.")
            
            # Save data
            with open('db/gamble/gamble_db.json', 'w') as file:
                json.dump(data, file)
            return
        else:
            user_balance = data[user_id]

        if user_balance <= 0:
            data[user_id] = -1 
            await ctx.respond(f"<@{user_id}>\nYou are bankrupt, there are no more opportunities for you :3 (game over)")
            return

        # Check if has enough money
        if user_balance < amount:
            await ctx.respond(f"<@{user_id}>\nYou poor :3.\nGamble with less money. You have `${user_balance}`.")
            return

        # GAMBLE TIME :D
        win = random.choice([True, False])

        if win:
            new_balance = user_balance + amount
            await ctx.respond(f"<@{user_id}>\nLMAOOOO YOU WON! Your new balance is **${new_balance}**.")
        else:
            new_balance = user_balance - amount
            await ctx.respond(f"<@{user_id}>\nYou lost! Your new balance is **${new_balance}**.")

        # Refresh db
        if new_balance <= 0:
            data[user_id] = -1 
            await ctx.followup.send(f"<@{user_id}>\nYou are bankrupt, there are no more opportunities for you :3 (game over)")
        else:
            data[user_id] = new_balance

        # Save data
        with open('db/gamble/gamble_db.json', 'w') as file:
            json.dump(data, file)

def setup(bot):
    bot.add_cog(gamble(bot))
