from typing import Optional
import aiohttp
import asyncio
from .. import SemantixGenClient


class Llama2InferenceClient(SemantixGenClient):
    def __init__(self, inference_server_id: str, api_secret: str, version: Optional[str]):
        super().__init__(inference_server_id, api_secret, version=version)
        self._type = "llama2"

    def generate(self, prompt: str, temperature: Optional[float] = None, top_p: Optional[int] = None, 
                      top_k: Optional[int] = None, max_new_tokens: Optional[int] = None, 
                      num_beams: Optional[int] = None):
        return asyncio.run(self._complete_async(prompt, temperature, top_p, top_k, max_new_tokens, num_beams))    

    async def _complete_async(self, prompt, temperature, top_p, top_k, max_new_tokens, num_beams):
        body = {
            "prompt": [prompt]
        }
        if temperature is not None:
            body["temperature"] = temperature
        if top_p is not None:
            body["top_p"] = top_p
        if top_k is not None:
            body["top_k"] = top_k
        if max_new_tokens is not None:
            body["max_new_tokens"] = max_new_tokens
        if num_beams is not None:
            body["num_beams"] = num_beams
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.url, json=body) as response:
                return await response.json()