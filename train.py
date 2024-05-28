import asyncio
import json
import re
import os

import llm
import util

from constants import USERS, MESSAGE_DB_PATH, MESSAGE_BATCH_SIZE, LLAMA_HOSTS


# =================================================================================================
# Global vars

username_to_name = {}
user_id_to_name = {}
for username, name, user_id, _ in USERS:
    username_to_name[username] = name
    user_id_to_name[user_id] = name

# =================================================================================================
# Analysis

async def analyse_traits(host, batch, person):
    rendered = render_messages(batch)
    return await llm.generate(host, f"You are reading a discord chat history. You will describe the personality and character traits of the person '{person}'. Your output will only be a single line and nothing else.", rendered)

async def analyse_facts(host, batch, person):
    rendered = render_messages(batch)
    return await llm.generate(host, f"You are reading a discord chat history. You will describe a list of facts about '{person}'. Each fact will be displayed on a line starting with '*'.", rendered)

async def find_best_example(host, batch, person):
    persons_messages = "\n".join([m[1] for m in batch if m[0] == person])
    return await llm.generate(host, f"Below is a list of messages sent by '{person}'. Find the one that best represents {person}'s texting style and repeat it below. You will not respond with anything except this single message.", persons_messages)

async def analyse_if_not_already(host, func, path, batch, person):
    util.create_dir_if_not_exists(os.path.dirname(path))

    if os.path.isfile(path):
        return

    res = await func(host, batch, person)

    print("==================")
    print(path)
    print(res)

    with open(path, "w") as f:
        f.write(res)


analysis_progress = 0
analysis_max_progress = 0
analysis_queue = []

def queue_analysis(analysis_func, write_path, batch, person):
    global analysis_max_progress
    analysis_queue.append((analysis_func, write_path, batch, person))
    analysis_max_progress += 1

async def queue_analyse_person(batch, person):
    batch_hash = util.md5(render_messages(batch))

    queue_analysis(analyse_traits, f"observations/{person}/traits/{batch_hash}", batch, person)
    queue_analysis(analyse_facts, f"observations/{person}/facts/{batch_hash}", batch, person)
    queue_analysis(find_best_example, f"observations/{person}/examples/{batch_hash}", batch, person)

async def complete_analysis_worker(host):
    global analysis_progress

    while len(analysis_queue) != 0:
        analysis_func, write_path, batch, person = analysis_queue.pop(0)

        await analyse_if_not_already(host, analysis_func, write_path, batch, person)

        analysis_progress += 1
        print(f"Progress update:\t{analysis_progress}/{analysis_max_progress} ({'{:.2f}'.format(100 * analysis_progress / analysis_max_progress)}%)")

async def complete_analysis():
    await asyncio.gather(
        *[complete_analysis_worker(h) for h in LLAMA_HOSTS]
    )

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

    for i, batch in enumerate(util.generate_batches(msg_db, MESSAGE_BATCH_SIZE)):
        users_in_batch = list(set([m[0] for m in batch]))

        for user in users_in_batch:
            await queue_analyse_person(batch, user)
    
    await complete_analysis()

    await llm.close()

asyncio.run(main())
