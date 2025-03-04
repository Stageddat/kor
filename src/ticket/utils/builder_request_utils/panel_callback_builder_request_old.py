import json
from datetime import datetime

import discord

from config import bot, guild_id
from src.utils.embed_to_dict import embed_to_dict
from src.global_src.global_channel_id import ticket_log_channel_id
from src.global_src.global_embed import error_embed, ticket_ban_embed
from src.global_src.global_path import (
        ticket_banned_path,
        ticket_cooldown_path,
        ticket_success_embed_path,
)
from src.global_src.global_roles import senior_moderator_role_id
from src.ticket.modal.form_builder_request import builder_request_modal
from src.ticket.utils.builder_request_utils.builder_ticket_type import ticket_type_dict
from src.ticket.utils.builder_request_utils.db_utils.add_db_builder_request import (
        add_builder_request_db,
)
from src.ticket.utils.builder_request_utils.db_utils.get_db_data_builder_request import (
        check_open_builder_ticket,
)
from src.ticket.utils.create_overwrites import create_custom_overwrites
from src.ticket.utils.gen_ticket_key import gen_key
from src.ticket.view.builder_request_views.form_builder_request import (
        form_builder_request_view,
)
from src.ticket.view.jump_channel import jump_channel

ticket_cooldown = 1

async def builder_request_panel_callback(button: discord.ui.Button, interaction: discord.Interaction, builder_type):
        # Get time
        open_time = int(datetime.now().timestamp())

        # Check if user is banned from tickets
        with open(ticket_banned_path, 'r') as f:
            data = json.load(f)

        if str(interaction.user.id) in data:
            await interaction.response.send_message(embed=ticket_ban_embed, ephemeral=True)
            return

        # Check if is in cooldown
        with open(ticket_cooldown_path, 'r') as f:
            data = json.load(f)
            last_time = data.get(str(interaction.user.id), "Not found")

        if last_time == "Not found":
            data[str(interaction.user.id)] = open_time
            with open(ticket_cooldown_path, 'w') as f:
                json.dump(data, f, indent=4)
        else:
            timeout_time = last_time + ticket_cooldown
            if open_time < timeout_time:
                await interaction.response.send_message("You're opening tickets so fast! Please wait a moment to open another one.", ephemeral=True)
                return
            else:
                data[str(interaction.user.id)] = open_time
                with open(ticket_cooldown_path, 'w') as f:
                    json.dump(data, f, indent=4)

        # Get ticket type:
        embed = [embed_to_dict(embed) for embed in interaction.message.embeds]
        ticket_title = embed[0]['title']
        ticket_data = ticket_type_dict[ticket_title]

        # Check user have current open channel
        open_ticket = check_open_builder_ticket(int(interaction.user.id), ticket_data['type'])
        try:
            if open_ticket is not False:
                ticket_id, channel_id = open_ticket
                embed = discord.Embed(
                    title=f"You already have an open {ticket_data['button_label']} ticket!",
                    description=f"You have the `{ticket_data['button_label']}` ticket: `{ticket_id}` already opened.\nYou can enter by clicking the button below.",
                    color=0xff0000
                )
                await interaction.response.send_message(embed=embed, view=jump_channel(guild_id, channel_id), ephemeral=True)
                return
        except Exception as e:
            error_code_embed = discord.Embed(
                title="Error code:",
                description=f"Error: ```{e}```\nTicket ID: `{ticket_id}`\nTime: <t:{int(datetime.now().timestamp())}:F>",
                colour=discord.Colour(int("ff0000", 16)),
            )
            await interaction.response.send_message(embeds=[error_embed, error_code_embed], ephemeral=True)
            print(f"Error when creating channel for ticket {ticket_id}: {e}")
            return

        # Defer response
        modal = builder_request_modal(title=f"{ticket_data['button_label']} Form", status="new", ticket_type=ticket_data['type'])
        await interaction.response.send_modal(modal)

        # Gen ticket id
        ticket_id = gen_key(15)

        # Get users and roles
        whoami = interaction.user
        ticket_role = interaction.guild.get_role(ticket_data['role_id'])
        moderator_role = interaction.guild.get_role(senior_moderator_role_id)

        # Set roles perms
        overwrites = create_custom_overwrites(
            interaction,
            no_perm_objects=(),
            view_only_objects=(whoami,),
            view_and_chat_objects=(
                ticket_role,
            ),
            moderator_objects=(
                moderator_role,
            ),
        )

        # Create ticket
        try:
            new_channel = await interaction.guild.create_text_channel(
                name=f"{interaction.user.name} - {ticket_data['short_name']}",
                overwrites=overwrites,
                topic=f"Ticket ID: {ticket_id}",
                reason=f"New channel for {ticket_data['button_label']} Builder request",
                category=discord.Object(id=ticket_data['category_id']),
            )

        except discord.errors.DiscordServerError as e:
            print(f"Error when creating channel for ticket {ticket_id}: {e}")
            error_code_embed = discord.Embed(
                title="Error code:",
                description=f"Error filter: **DISCORD INTERNAL SERVER ERROR**\nError: ```{e}```\nTicket ID: `{ticket_id}`\nTime: <t:{open_time}:F>",
                colour=discord.Colour(int("ff0000", 16)),
            )
            await interaction.followup.send(embeds=[error_embed, error_code_embed], ephemeral=True)
            print(f"Error when creating channel for ticket {ticket_id}: {e}")
            return

        except Exception as e:
            error_code_embed = discord.Embed(
                title="Error code:",
                description=f"Error: ```{e}```\nTicket ID: `{ticket_id}`\nTime: <t:{open_time}:F>",
                colour=discord.Colour(int("ff0000", 16)),
            )
            await interaction.followup.send(embeds=[error_embed, error_code_embed], ephemeral=True)
            print(f"Error when creating channel for ticket {ticket_id}: {e}")
            return

        # Send welcome message
        with open(ticket_data['welcome_embed_path'], "r", encoding="utf-8") as f:
            data = json.load(f)

        embed_info = data["embeds"][0]
        embed_info["title"] = embed_info["title"].replace("[USER]", interaction.user.name)
        embed_info["footer"]["text"] = embed_info["footer"]["text"].replace("[KEY]", ticket_id)
        embed = discord.Embed.from_dict(embed_info)

        welcome_message = await new_channel.send(
            f"{interaction.user.mention}", embed=embed, view=form_builder_request_view()
        )

        # Respond the message
        with open(ticket_success_embed_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for embed_info in data["embeds"]:
            embed = discord.Embed.from_dict(embed_info)

        channel_id = new_channel.id
        await interaction.followup.send(
            embed=embed, view=jump_channel(guild_id, channel_id), ephemeral=True
        )

        # Send DM
        try:    
            dm = await interaction.user.create_dm()
            with open(ticket_data['dm_embed_path'], "r", encoding="utf-8") as f:
                data = json.load(f)

            embed_info = data["embeds"][0]
            embed_info["footer"]["text"] = embed_info["footer"]["text"].replace("[KEY]", ticket_id)
            embed = discord.Embed.from_dict(embed_info)

            dm_message = await dm.send(
                content="", embed=embed, view=jump_channel(guild_id, channel_id)
            )
            dm_message_id = dm_message.id
        except discord.Forbidden:
            print(f"Failed send DM to {interaction.user.name}")
            dm_message_id = None

        # Send to log
        embed = discord.Embed(
            title=f"New {ticket_data['button_label']} ticket registered",
            description="Ticket details:",
            color=0xff8000,
        )
        embed.add_field(name="👤 User", value=f"{interaction.user.mention} ({interaction.user.id} - {interaction.user.name})", inline=False)
        embed.add_field(name="🆔 User ID", value=f"`{interaction.user.id}`", inline=False)
        embed.add_field(name="📛 User name", value=interaction.user.name, inline=False)
        embed.add_field(name="📅 Joined", value=f"<t:{int(interaction.user.joined_at.timestamp())}:R>", inline=False)
        embed.add_field(name="👥 Claim user", value="`No claimed`", inline=False)
        embed.add_field(name="📑 Open reason", value=f"```Request a {ticket_data['button_label']} Builder```", inline=False)
        embed.add_field(name="🕒 Open time", value=f"<t:{open_time}>", inline=False)
        embed.add_field(name="🏢 Ticket Channel", value=f"<#{channel_id}>", inline=False)
        embed.set_footer(text=f"Ticket ID: {ticket_id}")

        log_channel = bot.get_channel(ticket_log_channel_id)
        log_message = await log_channel.send(embed=embed)

        # Add data to database
        add_builder_request_db(
            ticket_id=ticket_id,
            ticket_type=ticket_data['type'],
            open_user_id=interaction.user.id,
            open_time=open_time,
            open_reason=f"Request a {ticket_data['button_label']} Builder",
            form_name=f"{interaction.user.mention} ({interaction.user.id} - {interaction.user.name})",
            form_roblox_user=None,
            form_island_code=None,
            form_build=None,
            form_build_desp=None,
            form_build_img=None,
            form_payment=None,
            channel_id=channel_id,
            welcome_msg_id=welcome_message.id,
            dm_msg_id=dm_message_id,
            confirm_message_id=None,
            queue_msg_id=None,
            log_msg_id=log_message.id,
            transcript_key = None,
            claim_user_id=None,
            close_user_id=None,
            close_time=None,
            close_reason=None,
        )