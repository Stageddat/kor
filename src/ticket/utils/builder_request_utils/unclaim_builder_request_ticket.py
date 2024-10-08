import re

import discord

from config import bot
from src.utils.embed_to_dict import embed_to_dict
from src.global_src.global_emojis import discord_emoji, roblox_emoji
from src.ticket.utils.builder_request_utils.builder_ticket_type import ticket_type_dict
from src.ticket.utils.builder_request_utils.db_utils.edit_db_builder_request import (
    edit_builder_request_db,
)
from src.ticket.utils.builder_request_utils.db_utils.get_db_data_builder_request import (
    get_builder_channel_id,
    get_builder_open_user_id,
    get_builder_queue_message_id,
    get_builder_ticket_type,
    get_builder_welcome_msg,
)
from src.ticket.utils.create_overwrites import create_custom_overwrites


async def unclaim_ticket(interaction: discord.Interaction, ticket_id = None):
    print(ticket_id)
    # Get ticket id
    if ticket_id is None:
        embed = [embed_to_dict(embed) for embed in interaction.message.embeds]
        ticket_id = {"origin": "button", "ticket_id":re.findall(r"Ticket ID: (\w+)", embed[0]["footer"]["text"])[0]}

    # Get ticket type
    ticket_type = get_builder_ticket_type(ticket_id=ticket_id["ticket_id"])
    for key, value in ticket_type_dict.items():
        if value["type"] == ticket_type:
            builder_role_id = value["role_id"]
            queue_channel_id = value["queue_channel_id"]
            builder_name = value["button_label"]

    # Get channel ID
    channel_id = get_builder_channel_id(ticket_id=ticket_id["ticket_id"])

    # Get open user ID
    open_user_id = get_builder_open_user_id(ticket_id=ticket_id["ticket_id"])

    # Get users and roles
    whoami = interaction.user
    open_user = bot.get_user(open_user_id)
    builder_role = interaction.guild.get_role(builder_role_id)

    # Set roles perms
    new_overwrites = create_custom_overwrites(
        interaction,
        no_perm_objects=(),
        view_only_objects=(),
        view_and_chat_objects=(
            whoami,
            open_user,
            builder_role,
        ),
        moderator_objects=(),
    )

    # Set new perms
    ticket_channel = bot.get_channel(channel_id)
    for obj, perms in new_overwrites.items():
        await ticket_channel.set_permissions(obj, overwrite=perms)

    # Respond and edit
    if ticket_id["origin"] == "button":
        await interaction.followup.send("Unclaimed!", ephemeral=True)
    elif ticket_id["origin"] == "cmd":
        await interaction.response.send_message("Unclaimed!", ephemeral=True)

    welcome_msg_id, channel_id = get_builder_welcome_msg(ticket_id=ticket_id["ticket_id"])
    welcome_msg = await bot.get_channel(channel_id).fetch_message(welcome_msg_id)
    from src.ticket.view.builder_request_views.actions_builder_request import (
        actions_builder_view,
    )
    await welcome_msg.edit(view=actions_builder_view())

    # Edit queue message
    try:
        queue_message_id = get_builder_queue_message_id(ticket_id=ticket_id["ticket_id"])
        if queue_message_id is not None:
            queue_message = await bot.get_channel(queue_channel_id).fetch_message(queue_message_id) # e
            old_embed = [embed_to_dict(embed) for embed in queue_message.embeds]
            
            new_embed = discord.Embed(
                title=f"{builder_name} ticket - {ticket_id['ticket_id']}",
                color=0xffa500,
                description=""
            )
            new_embed.add_field(name="👤 User", value=old_embed[0]['fields'][0]['value'], inline=False)
            new_embed.add_field(name="🆔 User ID", value=old_embed[0]['fields'][1]['value'], inline=False)
            new_embed.add_field(name="📛 User name", value=old_embed[0]['fields'][2]['value'], inline=False)
            new_embed.add_field(name="👥 Claim user", value="`No claimed`", inline=False)
            new_embed.add_field(name=f"{discord_emoji} Discord name", value=old_embed[0]['fields'][4]['value'], inline=False)
            new_embed.add_field(name=f"{roblox_emoji} Roblox username", value=old_embed[0]['fields'][5]['value'], inline=False)
            new_embed.add_field(name="🔢 Island Code", value=old_embed[0]['fields'][6]['value'], inline=False)
            new_embed.add_field(name="🏠 Build", value=old_embed[0]['fields'][7]['value'], inline=False)
            new_embed.add_field(name="💵 Payment", value=old_embed[0]['fields'][8]['value'], inline=False)
            new_embed.add_field(name="🏢 Channel", value=f"<#{channel_id}>", inline=False)
            new_embed.set_footer(text=old_embed[0]['footer']['text'])
            await queue_message.edit(embed=new_embed)
    except Exception as e:
        print(f"Failed edit unclaim queue message for ticket {ticket_id['ticket_id']}: {e}")

    notification_embed = discord.Embed(
            title="",
            description=f"{interaction.user.mention} unclaimed this ticket!",
            colour=discord.Colour(int("ff7900", 16)),
        )
    await interaction.channel.send(embed=notification_embed)
    # Save to database
    edit_builder_request_db(ticket_id=ticket_id["ticket_id"], claim_user_id=None)