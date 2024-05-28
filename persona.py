import os

import llm

async def respond_as_persona(persona, prompt):
    observations = []

    for fname in os.listdir(f"observations/{persona}"):
        with open(f"observations/{persona}/{fname}", "r") as f:
            observations.append(f.read())

    system = f"""You are pretending to be the user {persona}. Below is a list of descriptions of {persona}, as well as example text messages sent by {persona}:
{"\n".join(observations)}

You will respond to the following message as if you were {persona}. This includes copying {persona}'s character traits and trying to mimic the style of the example messages as accurately as possible."""
    
    return await llm.generate(system, prompt)
