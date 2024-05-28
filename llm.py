import aiohttp

global_sess = None

async def close():
    await global_sess.close()

async def generate(host, system, prompt):
    global global_sess
    if global_sess is None:
        global_sess = aiohttp.ClientSession()

    payload = {
        "model": "llama3",
        "system": system,
        "prompt": prompt,
        "stream": False
    }

    async with global_sess.post(f"{host}/api/generate", json=payload) as resp:
        data = await resp.json()
        return data["response"]