import os

import llm

from constants import USERS

name_to_pronoun = {}
for _, name, _, pronoun in USERS:
    name_to_pronoun[name] = pronoun

def get_persona_info(persona, info_type):
    info = []

    for fname in os.listdir(f"observations/{persona}/{info_type}"):
        with open(f"observations/{persona}/{info_type}/{fname}", "r") as f:
            info.append(f.read())
    
    return "\n".join(info)

async def respond_as_persona(persona, prompt):
    system = f"""You are pretending to be the person {persona}. The following data provides information on {persona}'s character traits:

{get_persona_info(persona, 'traits')}

The following data provides information on how {persona} relates to {name_to_pronoun[persona]} friends:

{get_persona_info(persona, 'relationships')}

To effectively mimic {persona}, you must copy their texting style including message length, capitalisation, and tone of voice. Below are some example messages sent by {persona} to copy from:

{get_persona_info(persona, 'examples')}"""
    
    return await llm.generate(system, prompt)
