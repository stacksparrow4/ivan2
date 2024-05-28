import os
import random

import llm
import util

from constants import USERS, LLAMA_HOSTS

target_host = LLAMA_HOSTS[-1]

user_names = [u[1] for u in USERS]
name_to_pronoun = {}
user_id_to_name = {}
for _, name, uid, pronoun in USERS:
    name_to_pronoun[name] = pronoun
    user_id_to_name[uid] = name

def read_all_files_in_dir(dir_path):
    info = []

    for fname in os.listdir(dir_path):
        with open(f"{dir_path}/{fname}", "r") as f:
            info.append(f.read())
    
    return "\n".join(info)

async def get_persona_traits(persona):
    with open(f"system/{persona}/traits", "r") as f:
        return f.read()

async def get_persona_facts(persona):
    return util.extract_dot_points(read_all_files_in_dir(f"system/{persona}/facts"))

async def get_persona_examples(persona):
    return "\n".join(random.sample(read_all_files_in_dir(f"observations/{persona}/examples").splitlines(), 20))

async def respond_as_persona(persona, author, prompt):
    system = f"""You are pretending to be the person {persona}. The following data provides information on {persona}'s character traits:

{await get_persona_traits(persona)}

Below is a list of facts about {persona}:

{await get_persona_facts(persona)}

Below is a list of example messages sent by {persona}:

{await get_persona_examples(persona)}

The following message was written by {author}. Respond to this message as if you were {persona}. Remember to copy {persona}'s texting style as shown in the examples."""
    
    print(system)

    return await llm.generate(LLAMA_HOSTS[-1], system, prompt)
