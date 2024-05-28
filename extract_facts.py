import asyncio
import os

import llm
import util
import messages

from constants import MESSAGE_BATCH_SIZE, LLAMA_HOSTS


async def extract_facts(host, path, batch, person):
    util.create_dir_if_not_exists(os.path.dirname(path))

    if os.path.isfile(path):
        return

    rendered = messages.render_messages(batch)
    res = await llm.generate(host, f"You are reading a discord chat history. You will describe a list of facts about '{person}'. Each fact will be displayed on a line starting with '*'.", rendered)

    print("==================")
    print(path)
    print(res)

    with open(path, "w") as f:
        f.write(res)

analysis_progress = 0
analysis_max_progress = 0
analysis_queue = []

async def queue_analyse_person(batch, person):
    batch_hash = util.md5(messages.render_messages(batch))

    global analysis_max_progress
    analysis_queue.append((f"observations/{person}/facts/{batch_hash}", batch, person))
    analysis_max_progress += 1

async def complete_analysis_worker(host):
    global analysis_progress

    while len(analysis_queue) != 0:
        path, batch, person = analysis_queue.pop(0)

        await extract_facts(host, path, batch, person)

        analysis_progress += 1
        print(f"Progress update:\t{analysis_progress}/{analysis_max_progress} ({'{:.2f}'.format(100 * analysis_progress / analysis_max_progress)}%)")

async def complete_analysis():
    await asyncio.gather(
        *[complete_analysis_worker(h) for h in LLAMA_HOSTS]
    )

async def main():
    msg_db = messages.load()

    for batch in util.generate_batches(msg_db, MESSAGE_BATCH_SIZE):
        users_in_batch = list(set([m[0] for m in batch]))

        for user in users_in_batch:
            await queue_analyse_person(batch, user)
    
    await complete_analysis()

    await llm.close()

asyncio.run(main())
