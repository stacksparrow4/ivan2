import os
import random

import llm
import util
import messages

msg_db, user_db = messages.load()

def read_all_files_in_dir(dir_path):
    info = []

    for fname in os.listdir(dir_path):
        with open(f"{dir_path}/{fname}", "r") as f:
            info.append(f.read())
    
    return "\n".join(info)

async def get_persona_facts(persona):
    return util.extract_dot_points(read_all_files_in_dir(f"collated/{persona}"))

async def get_persona_examples(persona):
    return "\n".join(random.sample([m[1] for m in msg_db if m[0] == persona], 40))

async def respond_as_persona(persona, prompt):
    system = f"""You are pretending to be the person '{persona}'. Below is a list of facts about '{persona}':

{await get_persona_facts(persona)}

Below is a list of example messages sent by '{persona}':

{await get_persona_examples(persona)}

Respond to the following message as if you were '{persona}'. Remember to copy the texting style of '{persona}' as shown in the examples."""

    return await llm.generate(os.environ.get("LLAMA_HOSTS").split(",")[0].strip(), system, prompt)
