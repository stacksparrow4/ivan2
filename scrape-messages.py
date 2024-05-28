import discord

import asyncio

import json

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guild_messages = True
intents.guilds = True

client = discord.Client(intents=intents)

is_ready = False

@client.event
async def on_ready():
    global is_ready
    is_ready = True

CHANNEL_IDS = [1159772223872176208, 1160494482958073876]

with open("token", "r") as f:
    token = f.read().strip()

async def main(token):
    await client.login(token)
    
    asyncio.create_task(client.connect())

    while not is_ready:
        await asyncio.sleep(0.1)

    msg_data = []

    for channel in CHANNEL_IDS:
        async for msg in client.get_channel(channel).history(limit=None):
            msg_data.append({"author": msg.author.name, "content": msg.content, "time": msg.created_at.timestamp()})
    
    with open("data/message-db.json", "w") as f:
        json.dump(msg_data, f)

asyncio.run(main(token))
