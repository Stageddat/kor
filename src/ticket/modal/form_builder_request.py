
import asyncio

import discord

from config import bot, guild_id
from src.global_src.global_emojis import loading_emoji
from src.ticket.utils.pixel_art_utils.db_utils.edit_db_pixel_art import (
    edit_db_pixel_art,
)
from src.ticket.utils.pixel_art_utils.db_utils.get_db_data_pixel_art import (
    check_open_pixel_art_ticket,
    get_pixel_art_confirm_message_id,
    get_pixel_art_welcome_msg,
)
from src.ticket.view.jump_channel import jump_channel
from src.ticket.view.pixel_art_views.confirm_form_pixel_art import (
    confirm_form_pixel_art_view,
)


class form_pixel_art_modal(discord.ui.Modal):
    def __init__(self, name, roblox_user=None, island_code=None, build=None, status=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.status = status

        self.add_item(discord.ui.InputText(
            label="Discord name",
            placeholder="Your discord name",
            min_length = 1,
            max_length = 30,
            style=discord.InputTextStyle.short,
            value=name
            ))

        self.add_item(discord.ui.InputText(
            label="Roblox username",
            placeholder="Your roblox username",
            min_length = 1,
            max_length = 30,
            style=discord.InputTextStyle.short,
            value=roblox_user
            ))

        self.add_item(discord.ui.InputText(
            label="Island code",
            placeholder="Your Roblox Island Code",
            min_length = 1,
            max_length = 10,
            style=discord.InputTextStyle.short,
            value=island_code
            ))

        self.add_item(discord.ui.InputText(
            label="What build you need?",
            placeholder="What build is in your mind?",
            min_length = 1,
            max_length = 400,
            row=3,
            style=discord.InputTextStyle.long,
            value=build
            ))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Pixel Art form answers",
            description="",
            color=0x28a745
            )

        embed.add_field(name="Discord name", value=f"```{self.children[0].value}```", inline=False)
        embed.add_field(name="Roblox username", value=f"```{self.children[1].value}```", inline=False)
        embed.add_field(name="Island Code", value=f"```{self.children[2].value}```", inline=False)
        embed.add_field(name="Build", value=f"```{self.children[3].value}```", inline=False)

        open_ticket = check_open_pixel_art_ticket(int(interaction.user.id))
        if open_ticket is False:
            loading_message = await interaction.response.send_message(f"{loading_emoji} Processing...", ephemeral=True)
            await asyncio.sleep(5)
            open_ticket = check_open_pixel_art_ticket(int(interaction.user.id))
            ticket_id, channel_id = open_ticket
            await loading_message.edit(content="Please, go to the ticket channel for proceed.", view=jump_channel(guild_id=guild_id, channel_id=channel_id))
        else:
            ticket_id, channel_id = open_ticket

        # Send form or edit
        if self.status == "new": # Send the message if is new form and change view in original welcome message
            welcome_msg_id, channel_id = get_pixel_art_welcome_msg(ticket_id)
            welcome_msg = await bot.get_channel(channel_id).fetch_message(welcome_msg_id)

            from src.ticket.view.pixel_art_views.actions_pixel_art import (
                actions_pixel_art_view,
            )
            await welcome_msg.edit(view=actions_pixel_art_view())
            confirm_message = await welcome_msg.reply(content="Please, confirm your answer before send to moderators", embed=embed, view=confirm_form_pixel_art_view())
            edit_db_pixel_art(ticket_id=ticket_id, confirm_message_id=confirm_message.id)
            try:
                await interaction.response.send_message("Please, go to the ticket channel for proceed", ephemeral=True, view=jump_channel(guild_id, channel_id))
            except Exception:
                pass

        elif self.status == "edit": # Edit if is trying edit the form
            confirm_message_id = get_pixel_art_confirm_message_id(ticket_id)
            confirm_message = await bot.get_channel(channel_id).fetch_message(confirm_message_id)
            await confirm_message.edit(content="Please, confirm your answer before send to moderators", embed=embed, view=confirm_form_pixel_art_view())
            await interaction.response.defer()
            return