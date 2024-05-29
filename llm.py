import aiohttp

from util import get_llama_hosts

global_sess = None
has_pulled = False

async def setup():
    global global_sess
    global_sess = aiohttp.ClientSession()

    print("Downloading llama3...")

    for h in get_llama_hosts():
        async with global_sess.post(f"{h}/api/pull", json={
            "name": "llama3",
            "stream": False
        }) as resp:
            assert (await resp.json())["status"] == "success"

        print("Download completed for", h)
    
    print("All downloads complete!")

async def close():
    await global_sess.close()

async def generate(host, system, prompt):
    payload = {
        "model": "llama3",
        "system": system,
        "prompt": prompt,
        "stream": False
    }

    async with global_sess.post(f"{host}/api/generate", json=payload) as resp:
        data = await resp.json()
        return data["response"]