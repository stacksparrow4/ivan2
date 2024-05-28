import asyncio

from dotenv import load_dotenv

load_dotenv(override=True)

import llm
import llm_queue
import util
import messages

MAX_FACT_GENERATIONS = 20
MIN_INPUT_LINES = 30
MESSAGE_CONTEXT = 5

def get_message_chains_by_user(msg_db, user):
    message_chains = []
    curr_chain = []

    for i, msg in enumerate(msg_db):
        is_msg_soon = any([m[0] == user for m in msg_db[i:i+MESSAGE_CONTEXT+1]])

        if is_msg_soon:
            curr_chain.append(msg)
        else:
            if len(curr_chain) > 0:
                curr_chain.extend(msg_db[i:i+MESSAGE_CONTEXT])
                message_chains.append(curr_chain)
                curr_chain = []
    
    if len(curr_chain) > 0:
        message_chains.append(curr_chain)
    
    return message_chains

async def main():
    msg_db, user_db = messages.load()

    queue = llm_queue.LLMQueue()

    for name in user_db.names():
        message_chains = get_message_chains_by_user(msg_db, name)
        if len(message_chains) == 0:
            continue
        
        # We want to join so that:
        # Firstly, each chunk is at least MIN_INPUT_LINES
        # Also there are no more than MAX_FACT_GENERATIONS

        while len(message_chains) > 1 and (
                any([len(chain) < MIN_INPUT_LINES for chain in message_chains]) 
                or len(message_chains) > MAX_FACT_GENERATIONS
            ):
            line_counts = [(i, len(chain)) for i, chain in enumerate(message_chains)]
            line_counts.sort(key=lambda _: _[1])
            first_ind = line_counts[0][0]
            second_ind = line_counts[1][0]
            lowest_line_count = message_chains.pop(first_ind)
            if first_ind < second_ind:
                second_ind -= 1
            second_lowest_line_count = message_chains.pop(second_ind)

            message_chains.append([*lowest_line_count, '---', *second_lowest_line_count])
        
        print(message_chains)


    # for batch in util.generate_n_chunks(msg_db, FACTS_BATCH_SIZE):
    #     rendered = messages.render_messages(batch)
    #     batch_hash = util.md5(rendered)
    #     users_in_batch = list(set([m[0] for m in batch]))

    #     for user in users_in_batch:
    #         queue.enqueue_job(f"observations/{user}/{batch_hash}", f"You are reading a discord chat history. You will describe a list of facts about '{user}'. Each fact will be displayed on a line starting with '*'.", rendered)
    
    # await queue.process_queue()

    # await llm.close()

asyncio.run(main())
