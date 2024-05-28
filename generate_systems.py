import asyncio
import os

import llm
import util

from constants import USERS, LLAMA_HOSTS

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

NUM_FACT_GENERATIONS = 10

async def queue_worker(host, queue):
    while len(queue) > 0:
        f_path, system, prompt = queue.pop(0)
        util.create_dir_if_not_exists(os.path.dirname(f_path))

        res = await llm.generate(host, system, prompt)

        with open(f_path, "w") as f:
            f.write(res)

async def main():
    queue = []

    for u in user_names:
        # Traits
        persona_traits = get_persona_info(u, 'traits')
        queue.append((f"system/{u}/traits", "Summarise the character traits listed. Provide as much detail as possible.", persona_traits))

        # Facts
        facts = util.extract_dot_points(get_persona_info(u, 'facts'))
        fact_lines = facts.splitlines()

        batch_size = len(fact_lines) // (NUM_FACT_GENERATIONS - 1)

        for i, batch in enumerate(util.generate_batches(fact_lines, batch_size)):
            queue.append((f"system/{u}/facts/{i}", f"Repeat the below facts about {u}, removing any that are unimportant.", "\n".join(batch)))
    
    await asyncio.gather(*[queue_worker(h, queue) for h in LLAMA_HOSTS])

asyncio.run(main())