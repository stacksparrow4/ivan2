import os

import discord

from dotenv import load_dotenv

load_dotenv(override=True)

import llm
import persona

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

msg_prefix = os.environ.get("COMMAND_PREFIX")
whitelisted_channels = [int(ch.strip()) for ch in os.environ.get("WHITELISTED_CHANNELS").split(",")]

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    
    await llm.setup()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith(msg_prefix):
        return

    if not message.channel.id in whitelisted_channels:
        return

    parts = message.content.split(maxsplit=2)
    if len(parts) == 3:
        chosen_persona = parts[1]
        
        if not chosen_persona in os.listdir("collated"):
            await message.reply("Available personas: " + " ".join(os.listdir("collated")))
            return
        
        async with message.channel.typing():
            resp = await persona.respond_as_persona(chosen_persona, parts[2])
        
        for emoji in message.guild.emojis:
            resp = resp.replace(f":{emoji.name}:", f"<:{emoji.name}:{emoji.id}>")

        await message.reply(resp)
    else:
        await message.reply(f"Usage: {msg_prefix} <PERSONA> <PROMPT>")

client.run(os.environ.get("BOT_TOKEN"))