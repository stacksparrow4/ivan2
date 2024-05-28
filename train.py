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
for username, name, user_id, _ in USERS:
    username_to_name[username] = name
    user_id_to_name[user_id] = name

# =================================================================================================
# Analysis

async def analyse_traits(rendered, person):
    return await llm.generate(f"You are reading a discord chat history. You will describe the personality and character traits of the person '{person}'. Your output will only be a single line and nothing else.", rendered)

async def analyse_relationships(rendered, person):
    return await llm.generate(f"You are reading a discord chat history. You will describe the way in which the person '{person}' relates to other people in the chat. Your output will only be a single line and nothing else.", rendered)

async def find_best_example(rendered, person):
    return await llm.generate(f"Below is a list of messages sent by '{person}'. Find the one that best represents {person}'s texting style and repeat it below. You will not respond with anything except this single message.", rendered)

async def analyse_if_not_already(path, func, rendered, person):
    util.create_dir_if_not_exists(os.path.dirname(path))

    if os.path.isfile(path):
        return

    res = await func(rendered, person)

    print("==================")
    print(path)
    print(res)

    with open(path, "w") as f:
        f.write(res)

async def analyse_person(msgs, person):
    rendered = render_messages(msgs)
    persons_messages = "\n".join([m[1] for m in msgs if m[0] == person])

    batch_hash = util.md5(rendered)

    await analyse_if_not_already(f"observations/{person}/traits/{batch_hash}", analyse_traits, rendered, person)
    await analyse_if_not_already(f"observations/{person}/relationships/{batch_hash}", analyse_relationships, rendered, person)
    await analyse_if_not_already(f"observations/{person}/examples/{batch_hash}", find_best_example, persons_messages, person)

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
    msg_db = load_message_db()
    msg_db = clean_message_db(msg_db)

    total_batches = len(msg_db) // MESSAGE_BATCH_SIZE + 1

    for i, batch in enumerate(util.generate_batches(msg_db, MESSAGE_BATCH_SIZE)):
        users_in_batch = list(set([m[0] for m in batch]))

        for user in users_in_batch:
            await analyse_person(batch, user)
        
        print(f"Progress update:\t{i}/{total_batches} ({'{:.2f}'.format(100 * i / total_batches)}%)")

    await llm.close()

asyncio.run(main())
