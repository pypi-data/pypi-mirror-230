from typing import Optional
import aiohttp
import asyncio
from .. import SemantixGenClient


class AlpacaInferenceClient(SemantixGenClient):
    def __init__(self, inference_server_id: str, api_secret: str, version: Optional[str]):
        super().__init__(inference_server_id, api_secret, version=version)
        self._type = "alpaca"

    def generate(self, prompt: str, temperature: Optional[float] = 0.1, top_k: Optional[int] = 80, 
                      top_p: Optional[int] = 40, num_beams: Optional[int] = 4, max_new_tokens: Optional[int] = 1024):
        return asyncio.run(self._complete_async(prompt, temperature, top_k, top_p, num_beams, max_new_tokens))

    async def _complete_async(self, prompt, temperature, top_k, top_p, num_beams, max_new_tokens):
        body = {
            "prompt": [prompt],
            "max_new_tokens": max_new_tokens,
            "top_p": top_p,
            "top_k": top_k,
            "num_beams": num_beams,
            "temperature": temperature,
        }
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(self.url, json=body) as response:
                return await response.json()