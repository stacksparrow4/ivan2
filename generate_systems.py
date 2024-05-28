import asyncio
import os

import llm
import llm_queue
import util

from constants import USERS

user_names = [u[1] for u in USERS]
name_to_pronoun = {}
user_id_to_name = {}
for _, name, uid, pronoun in USERS:
    name_to_pronoun[name] = pronoun
    user_id_to_name[uid] = name

def get_persona_info(persona, info_type):
    info = []

    for fname in os.listdir(f"observations/{persona}/{info_type}"):
        with open(f"observations/{persona}/{info_type}/{fname}", "r") as f:
            info.append(f.read())
    
    return "\n".join(info)

NUM_FACT_GENERATIONS = 30

async def main():
    queue = llm_queue.LLMQueue()

    for u in user_names:
        # Traits
        persona_traits = get_persona_info(u, 'traits')
        queue.enqueue_job(f"system/{u}/traits", "Summarise the character traits listed. Provide as much detail as possible.", persona_traits)

        # Facts
        facts = util.extract_dot_points(get_persona_info(u, 'facts'))
        fact_lines = facts.splitlines()

        batch_size = len(fact_lines) // (NUM_FACT_GENERATIONS - 1)

        for i, batch in enumerate(util.generate_batches(fact_lines, batch_size)):
            queue.enqueue_job(f"system/{u}/facts/{i}", f"Repeat the below facts about {u}, removing any that are unimportant.", "\n".join(batch))
    
    await queue.process_queue(recompute=True)

    await llm.close()

asyncio.run(main())