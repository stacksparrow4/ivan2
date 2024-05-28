import os
import asyncio

import llm
import util

class LLMQueue:
    def __init__(self, debug=True):
        self.ind = 0
        self.last_progress = 0
        self.queue = []
        self.debug = debug
    
    def enqueue_job(self, path, system, prompt):
        self.queue.append((path, system, prompt))
    
    async def process_queue_with_host(self, host, recompute):
        while self.ind < len(self.queue):
            path, system, prompt = self.queue[self.ind]
            self.ind += 1

            util.create_dir_if_not_exists(os.path.dirname(path))

            if recompute or not os.path.isfile(path):
                res = await llm.generate(host, system, prompt)

                if self.debug:
                    print("====================")
                    print(path)
                    print(res)

                with open(path, "w") as f:
                    f.write(res)
                
                curr_prog = (100 * self.ind) // len(self.queue)
                if curr_prog != self.last_progress:
                    print(f"{curr_prog}%")
            
            self.last_progress = (100 * self.ind) // len(self.queue)

    async def process_queue(self, recompute=False):
        assert self.ind == 0

        await asyncio.gather(*[self.process_queue_with_host(host, recompute) for host in os.environ.get("LLAMA_HOSTS")])