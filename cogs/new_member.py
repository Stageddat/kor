import discord
from discord.commands import Option
from discord.ext import commands
from src.global_src.global_embed import no_perm_embed

from config import bot
from src.global_src.global_channel_id import new_members_log_channel_id
from src.global_src.global_roles import (
    assistant_director_role_id,
    community_manager_role_id,
    developer_role_id,
    head_of_operations_role_id,
    owner_role_id,
    staff_manager_role_id,
)
from src.new_member.create_welcome_card import create_welcome_card


class new_member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        log_channel = bot.get_channel(new_members_log_channel_id)

        embed = discord.Embed(
            title="",
            description=f"{member.mention} ({member.id}) joined!",
            colour=discord.Colour(int("24a424", 16))
        )
        await log_channel.send(embed=embed)
        await create_welcome_card(member)

    @discord.slash_command(name = "test_welcome", description = "Test the welcome feature with specifig member")
    async def test_welcome(self, ctx: discord.ApplicationContext, member: Option(discord.Member, "Test subject :D")):# type: ignore
        await ctx.defer(ephemeral=True)
        if int(ctx.author.id) != 756509638169460837 and not any(role.id in [
                staff_manager_role_id,
                community_manager_role_id,
                assistant_director_role_id,
                head_of_operations_role_id,
                developer_role_id,
                owner_role_id] for role in ctx.author.roles):
            await ctx.respond(embed=no_perm_embed, ephemeral=True)
            return
        await create_welcome_card(member)
        await ctx.respond("Done xd")

def setup(bot):
    bot.add_cog(new_member(bot))