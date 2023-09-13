from .. import CohereClient
import aiohttp
import asyncio
from typing import List, Optional

class CohereInferenceClient(CohereClient):
    def __init__(self, api_key: Optional[str]=None, 
                 generate_model: Optional[str] = "command",
                 version: Optional[str] = "v1"):
        super().__init__(api_key, generate_model, version)
        self._type = "cohere"

    def generate(self, prompt: str, 
                    num_generations: Optional[int]=None, 
                    stream: Optional[bool]=None,
                    max_tokens: Optional[int]=None, 
                    truncate: Optional[str]=None, 
                    temperature: Optional[float]=None, 
                    preset: Optional[str]=None, 
                    end_sequences: Optional[List[str]]=None, 
                    stop_sequences: Optional[List[str]]=None, 
                    k: Optional[int]=None, p: Optional[float]=None, 
                    frequency_penalty: Optional[float]=None, 
                    presence_penalty: Optional[float]=None, 
                    return_likelihoods: Optional[str]=None, 
                    logit_bias: Optional[dict]=None):
        return asyncio.run(self._generate_async(prompt, 
                                                num_generations, 
                                                stream, max_tokens, 
                                                truncate, 
                                                temperature, preset, 
                                                end_sequences, 
                                                stop_sequences, 
                                                k, p, frequency_penalty, 
                                                presence_penalty, 
                                                return_likelihoods, 
                                                logit_bias))
        
    async def _generate_async(self, prompt, num_generations,
                        stream, max_tokens, truncate, 
                        temperature, preset, end_sequences,
                        stop_sequences, k, p, frequency_penalty,
                        presence_penalty, return_likelihoods, logit_bias):
        body = {
            "prompt": prompt,
        }
        # iterate over all optional arguments and add them to the body if they are not None
        for key, value in locals().items():
            if key == "self" or key == "prompt" \
                or value is None or key == "body":
                continue
            body[key] = value
        url = f"{self._host}/{self._version}/generate"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=body) as response:
                return await response.json()

