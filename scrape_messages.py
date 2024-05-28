import asyncio
import json
import os

import discord

from dotenv import load_dotenv

import util

load_dotenv(override=True)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_messages = True
intents.guilds = True

client = discord.Client(intents=intents)

CHANNEL_IDS = [int(ch_id.strip()) for ch_id in os.environ.get("SCRAPE_CHANNELS").split(",")]

@client.event
async def on_ready():
    print("Starting pull...")

    msg_data = []

    users = {}

    for channel in CHANNEL_IDS:
        async for msg in client.get_channel(channel).history(limit=None, oldest_first=True):
            msg_data.append({"author": msg.author.name, "content": msg.content, "time": msg.created_at.timestamp()})
            users[msg.author.name] = {
                "name": msg.author.display_name,
                "id": str(msg.author.id)
            }
    
    util.write_to_path("data/message-db.json", json.dumps(msg_data))
    util.write_to_path("data/users.json", json.dumps(users))

    print("Finished!")

    await client.close()

client.run(os.environ.get("BOT_TOKEN"))