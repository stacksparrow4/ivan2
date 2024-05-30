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

MAX_MESSAGE_HIST = 100

# Structure: [(message_id, persona, [(user_msg, bot_msg), ...]), ...]
msg_hist = []

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    chosen_persona = None
    history = None
    prompt = ""
    if message.reference is not None:
        matches = [m for m in msg_hist if m[0] == message.reference.message_id]

        if len(matches) > 0:
            chosen_persona = matches[0][1]
            history = matches[0][2]
            prompt = message.content
        else:
            return
    else:
        if not message.content.startswith(msg_prefix):
            return

        if not message.channel.id in whitelisted_channels:
            return

        parts = message.content.split(maxsplit=2)
        if len(parts) != 3:
            await message.reply(f"Usage: {msg_prefix} <PERSONA> <PROMPT>")
            return
        
        chosen_persona = parts[1]
        prompt = parts[2]
    
    for allowed_persona in os.listdir("collated"):
        if chosen_persona.lower() == allowed_persona.lower():
            chosen_persona = allowed_persona
            break
    else:
        await message.reply("Available personas: " + " ".join(os.listdir("collated")))
        return
    
    async with message.channel.typing():
        resp = await persona.respond_as_persona(chosen_persona, prompt, history)
    
    emojified_resp = resp

    for emoji in message.guild.emojis:
        emojified_resp = emojified_resp.replace(f":{emoji.name}:", f"<:{emoji.name}:{emoji.id}>")

    sent_msg = await message.reply(emojified_resp)

    while len(msg_hist) >= MAX_MESSAGE_HIST:
        msg_hist.pop(0)
    
    msg_hist.append((sent_msg.id, chosen_persona, ([] if history is None else history) + [(prompt, resp)]))

client.run(os.environ.get("BOT_TOKEN"))