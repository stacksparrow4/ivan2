import os

import llm

async def respond_as_persona(persona, prompt):
    observations = []

    for fname in os.listdir(f"observations/{persona}"):
        with open(f"observations/{persona}/{fname}", "r") as f:
            observations.append(f.read())

    system = f"""You are pretending to be the user {persona}. Here are some attributes about {persona}:
{"\n".join(observations)}

You will respond to the following message as if you were {persona}."""
    
    return await llm.generate(system, prompt)
