import aiohttp
import asyncio
import json
import re
import hashlib
import os

from pathlib import Path

# =================================================================================================
# Constants

LLAMA_HOST = 'http://localhost:11434'
MESSAGE_DB_PATH = "data/message-db.json"

USERS = [
    ("ssparrow", "Daniel", 485713672161722379),
    ("mimedc", "Pri", 772428196191666187),
    ("kitkadesa", "Nat", 180220266272653312),
    ("merlune", "Helen", 655635072309002252),
    ("itsironiciinsist", "Zac", 315013788342419457),
    ("babybeefier", "Colleen", 219061332442349568)
]

MESSAGE_BATCH_SIZE = 100

# =================================================================================================
# Global vars

global_sess = None

username_to_name = {}
user_id_to_name = {}
for username, name, user_id in USERS:
    username_to_name[username] = name
    user_id_to_name[user_id] = name

# =================================================================================================
# Utils

def create_dir_if_not_exists(dir_name):
    Path(dir_name).mkdir(parents=True, exist_ok=True)

def md5(data):
    return hashlib.md5(data.encode()).hexdigest()

def generate_batches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

# =================================================================================================
# Llama

async def generate_llm(system, prompt):
    payload = {
        "model": "llama3",
        "system": system,
        "prompt": prompt,
        "stream": False
    }

    async with global_sess.post(f"{LLAMA_HOST}/api/generate", json=payload) as resp:
        data = await resp.json()
        return data["response"]

async def describe_person(msgs, person):
    return await generate_llm(f"You are reading a discord chat history. You will output a description of the person '{person}' and nothing else.", render_messages(msgs))

# =================================================================================================
# Messages

def load_message_db():
    with open(MESSAGE_DB_PATH, "r") as f:
        return json.load(f)

def clean_message_db(msg_db):
    for m in msg_db:
        m["content"] = re.sub(r"<(:[^:]+:)[0-9]+>", r"\1", m["content"])
        for uid in user_id_to_name:
            m["content"] = m["content"].replace(f"<@{uid}>", f"@{user_id_to_name[uid]}")

    return [
        (username_to_name[m["author"]], m["content"])
        for m in msg_db
        if m['content'] and m['author'] in username_to_name.keys()
    ]

def render_messages(msgs):
    return "\n".join([": ".join(msg) for msg in msgs])

# =================================================================================================
# Main

async def main():
    for _, name, _ in USERS:
        create_dir_if_not_exists(f"observations/{name}")

    msg_db = load_message_db()
    msg_db = clean_message_db(msg_db)

    total_batches = len(msg_db)//MESSAGE_BATCH_SIZE + 1

    for i, batch in enumerate(generate_batches(msg_db, MESSAGE_BATCH_SIZE)):
        batch_hash = md5(render_messages(batch))
        users_in_batch = list(set([m[0] for m in batch]))

        for user in users_in_batch:
            f_path = f"observations/{user}/{batch_hash}"

            if os.path.isfile(f_path):
                print(f"Skipping:\t{f_path}")
                continue

            desc = await describe_person(batch, user)
            with open(f_path, "w") as f:
                f.write(desc)
            
            print(f"Generated:\t{f_path}")
        
        print(f"Progress update:\t{i}/{total_batches} ({'{:.2f}'.format(100 * i / total_batches)}%)")

async def main_wrapper():
    global global_sess
    global_sess = aiohttp.ClientSession()
    
    await main()

    await global_sess.close()

asyncio.run(main_wrapper())
