from config import *
from discord.commands import Option
from src.new_member.create_welcome_card import create_welcome_card, send_welcome_message_and_DM
from src.global_embeds import *

class new_member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        log_channel = bot.get_channel(new_members_log_channel_id)

        print(f"{member} joined")
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
                staff_manager,
                community_manager,
                assistant_director,
                head_of_operations,
                developer,
                mr_boomsteak] for role in ctx.author.roles):
            await ctx.respond(embed=no_perm_embed, ephemeral=True)
            return
        await create_welcome_card(member)
        await ctx.respond("Done xd")

def setup(bot):
    bot.add_cog(new_member(bot))