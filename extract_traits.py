import asyncio

import llm
import llm_queue
import util
import messages

from constants import TRAITS_BATCH_SIZE

async def main():
    msg_db = messages.load()

    queue = llm_queue.LLMQueue()

    for batch in util.generate_batches(msg_db, TRAITS_BATCH_SIZE):
        rendered = messages.render_messages(batch)
        batch_hash = util.md5(rendered)
        users_in_batch = list(set([m[0] for m in batch]))

        for user in users_in_batch:
            queue.enqueue_job(f"observations/{user}/traits/{batch_hash}", f"You are reading a discord chat history. You will describe a list of personality and character traits of the person '{user}'. Each trait will be displayed on a line starting with '*'.", rendered)
    
    await queue.process_queue()

    await llm.close()

asyncio.run(main())
