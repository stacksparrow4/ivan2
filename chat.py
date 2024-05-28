import asyncio
import readline

import persona
import llm

async def main():
    await llm.init()
    while 1:
        try:
            print(await persona.respond_as_persona("Daniel", input("> ")))
        except EOFError:
            break
    await llm.close()

asyncio.run(main())