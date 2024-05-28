import asyncio
import os

import dotenv

dotenv.load_dotenv(override=True)

import llm
import llm_queue
import util

def get_persona_info(persona, info_type):
    info = []

    for fname in os.listdir(f"observations/{persona}/{info_type}"):
        with open(f"observations/{persona}/{info_type}/{fname}", "r") as f:
            info.append(f.read())
    
    return "\n".join(info)

NUM_FACT_GENERATIONS = 20

async def main():
    queue = llm_queue.LLMQueue()

    for name in os.listdir("observations"):
        # Facts
        facts = []
        for observation in os.listdir(f"observations/{name}"):
            with open(f"observations/{name}/{observation}", "r") as f:
                facts.append(f.read())
        facts_lines = "\n".join(facts).splitlines()

        for i, batch in enumerate(util.generate_n_batches(facts_lines, NUM_FACT_GENERATIONS)):
            queue.enqueue_job(f"collated/{name}/{i}", f"Repeat the below facts about '{name}', removing any that are unimportant.", "\n".join(batch))
    
    await queue.process_queue(recompute=True)

    await llm.close()

asyncio.run(main())