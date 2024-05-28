import aiohttp

from constants import LLAMA_HOST

global_sess = None

async def init():
    global global_sess
    global_sess = aiohttp.ClientSession()

async def close():
    await global_sess.close()

async def generate(system, prompt):
    payload = {
        "model": "llama3",
        "system": system,
        "prompt": prompt,
        "stream": False
    }

    async with global_sess.post(f"{LLAMA_HOST}/api/generate", json=payload) as resp:
        data = await resp.json()
        return data["response"]