import asyncio
import json
import re
import os

import llm
import util

from constants import USERS, MESSAGE_DB_PATH, MESSAGE_BATCH_SIZE


# =================================================================================================
# Global vars

username_to_name = {}
user_id_to_name = {}
for username, name, user_id in USERS:
    username_to_name[username] = name
    user_id_to_name[user_id] = name

# =================================================================================================
# LLM

async def describe_person(msgs, person):
    return await llm.generate(f"You are reading a discord chat history. You will output a description of the person '{person}'. After the description, you will also output a single example message that represents {person}'s texting style.", render_messages(msgs))

# =================================================================================================
# Messages

def load_message_db():
    with open(MESSAGE_DB_PATH, "r") as f:
        return json.load(f)

def clean_message_db(msg_db):
    for m in msg_db:
        m["content"] = re.sub(r"<a?(:[^:]+:)[0-9]+>", r"\1", m["content"])
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
        util.create_dir_if_not_exists(f"observations/{name}")

    msg_db = load_message_db()
    msg_db = clean_message_db(msg_db)

    total_batches = len(msg_db) // MESSAGE_BATCH_SIZE + 1

    for i, batch in enumerate(util.generate_batches(msg_db, MESSAGE_BATCH_SIZE)):
        batch_hash = util.md5(render_messages(batch))
        users_in_batch = list(set([m[0] for m in batch]))

        for user in users_in_batch:
            f_path = f"observations/{user}/{batch_hash}"

            if os.path.isfile(f_path):
                print(f"Skipping:\t{f_path}")
                continue

            desc = await describe_person(batch, user)
            with open(f_path, "w") as f:
                print(desc)
                f.write(desc)
            
            print(f"Generated:\t{f_path}")
        
        print(f"Progress update:\t{i}/{total_batches} ({'{:.2f}'.format(100 * i / total_batches)}%)")

async def main_wrapper():
    await llm.init()
    
    await main()

    await llm.close()

asyncio.run(main_wrapper())
