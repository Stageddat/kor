import json
import os
import sqlite3

import discord
import dotenv
import requests

from config import bot
from src.global_src.embed_to_dict import embed_to_dict
from src.global_src.global_channel_id import ticket_transcript_forum_id
from src.global_src.global_path import ticket_database_path
from src.ticket.utils.pixel_art_utils.db_utils.edit_db_pixel_art import edit_db_pixel_art

dotenv.load_dotenv()
webhook_link = str(os.getenv("WEBHOOK_LINK"))

def send_discord_message(profile, thread_id, name, message_content, embeds):
    webhook_url = f"{webhook_link}?thread_id={thread_id}"
    # Message format
    data = {
        "avatar_url": profile,
        "username": name,
        "content": message_content,
        "embeds": [embed_to_dict(embed) for embed in embeds]
    }

    # Send msg
    response = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    if response.status_code != 204:
        raise ValueError(f"Request to Discord returned an error {response.status_code}: {response.text}.")

async def webhook_transcript(message: discord.Message):
    # Connect to the database
    conn = sqlite3.connect(ticket_database_path)
    cursor = conn.cursor()

    # Check if the ticket has a transcript_thread_id and get others information
    cursor.execute('SELECT transcript_thread_id, ticket_id, open_user_id FROM pixel_art WHERE channel_id = ?', (message.channel.id,))
    ticket = cursor.fetchone()

    # Close the database connection
    conn.close()

    # Save variables
    if ticket is not None:
        transcript_thread_id = ticket[0]
        ticket_id = ticket[1]
        open_user_id = ticket[2]
    else:
        print(f"Ticket {ticket_id} information not found.")


    user = bot.get_user(message.author.id)
    if user.avatar:
        pfp_url = str(user.avatar.url)
    else:
        pfp_url = "https://discord.com/assets/1f0bfc0865d324c2587920a7d80c609b.png"

    log_channel = bot.get_channel(ticket_transcript_forum_id)

    # Check if the ticket has a transcript_thread_id
    if transcript_thread_id is not None:
        if message.content == "" and not message.embeds:
            print("Empty message. Ignoring...")
            return
        send_discord_message(pfp_url, transcript_thread_id, user.name, message.content, message.embeds) # Ticket have thread

    else:
        open_user = bot.get_user(open_user_id) # Ticket dont have thread
        thread = await log_channel.create_thread(name=f"Pixel Art Request - {ticket_id} - {open_user.name}", content="Starting new transcript...")
        if message.content == "" and not message.embeds:
            print("Empty message. Ignoring...")
            return
        send_discord_message(pfp_url, thread.id, user.name, message.content, message.embeds)
        print(thread.id)
        edit_db_pixel_art(
        ticket_id=ticket_id,
        transcript_thread_id=thread.id,
        )