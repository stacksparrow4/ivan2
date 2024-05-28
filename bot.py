import discord

import persona

from constants import USERS, ALLOWED_CHANNELS

user_names = [u[1] for u in USERS]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(".cook"):
        return

    if not message.channel.id in ALLOWED_CHANNELS:
        return

    parts = message.content.split(maxsplit=2)
    if len(parts) == 3:
        matched_persona = None
        for u in user_names:
            if u.lower() == parts[1].lower():
                matched_persona = u
                break
        else:
            await message.reply("Available personas: " + " ".join(user_names))
            return
        
        async with message.channel.typing():
            resp = await persona.respond_as_persona(matched_persona, parts[2])
        
        for emoji in message.guild.emojis:
            resp = resp.replace(f":{emoji.name}:", f"<:{emoji.name}:{emoji.id}>")

        await message.reply(resp)
    else:
        await message.reply("Usage: .cook <PERSONA> <MESSAGE>")

with open("token", "r") as f:
    token = f.read().strip()
client.run(token)