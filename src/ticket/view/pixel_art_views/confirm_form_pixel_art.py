import re

import discord

from config import bot
from src.global_src.embed_to_dict import embed_to_dict
from src.global_src.global_embed import no_perm_embed
from src.global_src.global_emojis import send_emoji
from src.ticket.utils.create_overwrites import create_view_and_chat_overwrites
from src.ticket.utils.db_utils.edit_db_pixel_art import edit_db_pixel_art
from src.ticket.utils.db_utils.get_db_data_pixel_art import (
    get_open_user_id,
    get_welcome_msg,
)


class confirm_form_pixel_art_view(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Send!", style=discord.ButtonStyle.green, emoji=send_emoji, custom_id="send_form_pixel_art_view")
    async def send_form_pixel_art_view(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Get ticket ID
        ticket_id = re.findall(r"Ticket ID: (\w+)", interaction.channel.topic)[0]

        # Verify user
        open_user_id = get_open_user_id(ticket_id)
        if int(interaction.user.id) != int(open_user_id):
            await interaction.response.send_message(embed=no_perm_embed, ephemeral=True)

        # Get form data
        embed = [embed_to_dict(embed) for embed in interaction.message.embeds]
        name = embed[0]['fields'][0]['value'].replace("```", "")
        roblox_username = embed[0]['fields'][1]['value'].replace("```", "")
        island_code = embed[0]['fields'][2]['value'].replace("```", "")
        build = embed[0]['fields'][3]['value'].replace("```", "")
        edit_db_pixel_art(
            ticket_id=ticket_id,
            form_name=name,
            form_roblox_user=roblox_username,
            form_island_code=island_code,
            form_build=build,
        )

        # Respond and delete self message
        embed = discord.Embed(
            title="Thank you for complete the form!",
            description="Please, wait our <@{ROLEE}> contact you.\nYou can now send a **image** of the construction that you want!",
            color=0x28a745
        )
        await interaction.response.send_message(embed=embed)
        await interaction.message.delete(reason=f"Deleting form confirm message from the ticket {ticket_id}")

        welcome_msg_id, channel_id = get_welcome_msg(ticket_id)
        welcome_msg = await bot.get_channel(channel_id).fetch_message(welcome_msg_id)

        new_welcome_embed = discord.Embed(
            title=f"Welcome {interaction.user.name}",
            description="Please wait for a member of the staff to contact you.\n\n## Form information",
            color=0x58B9FF
        )
        new_welcome_embed.add_field(name="Discord name", value=f"```{name}```", inline=False)
        new_welcome_embed.add_field(name="Roblox username", value=f"```{roblox_username}```", inline=False)
        new_welcome_embed.add_field(name="Island Code", value=f"```{island_code}```", inline=False)
        new_welcome_embed.add_field(name="Build", value=f"```{build}```", inline=False)
        new_welcome_embed.set_footer(text=f"Ticket ID: {ticket_id}")
        await welcome_msg.edit(content="", embed=new_welcome_embed)

        # Give perm for chat to user
        new_overwrites = create_view_and_chat_overwrites(
            interaction, interaction.user,
        )
        ticket_channel = bot.get_channel(interaction.channel.id)
        await ticket_channel.set_permissions(interaction.user, overwrite=new_overwrites[interaction.user])

        # Advise ticket to mods
        pixel_art_queue_channel = bot.get_channel(1222959134455107585)
        embed = discord.Embed(
            title=f"New pixel art ticket - {interaction.user.id}",
            color=0xffa500,
            description=f"""
            User: {interaction.user.mention}
            User ID: `{interaction.user.id}`
            User name: {interaction.user.name}
            Joined <t:{int(interaction.user.joined_at.timestamp())}:R>
            Claim users: `No claimed`
            ## Form answers""",
        )
        embed.add_field(name="Discord name", value=f"```{name}```", inline=False)
        embed.add_field(name="Roblox username", value=f"```{roblox_username}```", inline=False)
        embed.add_field(name="Island Code", value=f"```{island_code}```", inline=False)
        embed.add_field(name="Build", value=f"```{build}```", inline=False)
        embed.set_footer(text=f"Ticket ID: {ticket_id}")
        from src.ticket.view.pixel_art_views.actions_pixel_art import actions_pixel_art_view
        await pixel_art_queue_channel.send("<@&1222579667207192626>", embed=embed, view=actions_pixel_art_view())

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, emoji="✏️", custom_id="edit_form_pixel_art_view")
    async def edit_form_pixel_art_view(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Get ticket ID
        ticket_id = re.findall(r"Ticket ID: (\w+)", interaction.channel.topic)[0]

        # Verify user
        open_user_id = get_open_user_id(ticket_id)
        if int(interaction.user.id) != int(open_user_id):
            await interaction.response.send_message(embed=no_perm_embed, ephemeral=True)

        # Get old data
        embed = [embed_to_dict(embed) for embed in interaction.message.embeds]
        name = embed[0]['fields'][0]['value'].replace("```", "")
        roblox_username = embed[0]['fields'][1]['value'].replace("```", "")
        island_code = embed[0]['fields'][2]['value'].replace("```", "")
        build = embed[0]['fields'][3]['value'].replace("```", "")

        # Send modal
        from src.ticket.modal.form_pixel_art import form_pixel_art_modal
        modal = form_pixel_art_modal(title="Pixel Art Form", name=name, status="edit", roblox_user=roblox_username, island_code=island_code, build=build)
        await interaction.response.send_modal(modal)