import os
import re

import llm

from constants import USERS

name_to_pronoun = {}
for _, name, _, pronoun in USERS:
    name_to_pronoun[name] = pronoun

def extract_dot_points(data):
    new_lines = []
    for l in data.splitlines():
        if re.match(r"^(\*|[0-9]+\.) ", l):
            new_lines.append(re.sub(r"^[0-9]+\. ", "* ", l))
    return "\n".join(new_lines)

def get_persona_info(persona, info_type):
    info = []

    for fname in os.listdir(f"observations/{persona}/{info_type}"):
        with open(f"observations/{persona}/{info_type}/{fname}", "r") as f:
            info.append(f.read())
    
    return "\n".join(info)

async def respond_as_persona(persona, prompt):
    facts = extract_dot_points(get_persona_info(persona, 'facts'))

    system = f"""You are pretending to be the person {persona}. The following data provides information on {persona}'s character traits:

{get_persona_info(persona, 'traits')}

Below is a list of facts about {persona}:

{facts}

The following data provides information on how {persona} relates to {name_to_pronoun[persona]} friends:

{get_persona_info(persona, 'relationships')}

Below is a list of example messages sent by {persona}:

{get_persona_info(persona, 'examples')}

Respond to the following prompt as if you are {persona}. Remember to copy {persona}'s message length, capitalisation, and tone of voice."""
    
    return await llm.generate(system, prompt)
