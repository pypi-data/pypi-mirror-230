from .. import OpenAIClient
import aiohttp
import asyncio
from typing import List, Optional, Union

class OpenAIInferenceClient(OpenAIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type = "openai"
    
    async def _generate_async(self, messages, 
                                functions=None,
                                function_call=None,
                                temperature=None,
                                top_p=None,
                                n=None,
                                stop=None,
                                max_tokens=None,
                                presence_penalty=None,
                                frequency_penalty=None,
                                logit_bias=None,
                                user=None):
        body = {
            "messages": messages,
            "model": self._model,
        }
        # iterate over all optional arguments and add them to the body if they are not None
        for key, value in locals().items():
            if key == "self" or key == "messages" \
                or value is None or key == "body":
                continue
            body[key] = value
        url = f"{self._host}/{self._version}/chat/completions"

        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=body) as response:
                yield await response.json()

    def generate(self, messages: List[dict], functions: Optional[List[dict]]=None, 
                    function_call: Optional[str]=None,
                    temperature: Optional[float]=None, 
                    top_p: Optional[float]=None, 
                    n: Optional[int]=None, 
                    stop: Optional[Union[str, List[str]]]=None, 
                    max_tokens: Optional[int]=None, 
                    presence_penalty: Optional[float]=None, 
                    frequency_penalty: Optional[float]=None, 
                    logit_bias: Optional[dict]=None, 
                    user: Optional[str]=None):
        return asyncio.run(self._generate_async(messages, functions, function_call, temperature, top_p, n, stop, max_tokens,
                                                presence_penalty, frequency_penalty, logit_bias, user))

    async def generate_stream(self, messages: List[dict], functions: Optional[List[dict]]=None, 
                    function_call: Optional[str]=None,
                    temperature: Optional[float]=None, 
                    top_p: Optional[float]=None, 
                    n: Optional[int]=None, 
                    stop: Optional[Union[str, List[str]]]=None, 
                    max_tokens: Optional[int]=None, 
                    presence_penalty: Optional[float]=None, 
                    frequency_penalty: Optional[float]=None, 
                    logit_bias: Optional[dict]=None, 
                    user: Optional[str]=None):
        body = {
            "messages": messages,
            "stream": True,
            "model": self._model,
        }
        # iterate over all optional arguments and add them to the body if they are not None
        for key, value in locals().items():
            if key == "self" or key == "messages" \
                or value is None or key == "body":
                continue
            body[key] = value
        url = f"{self._host}/{self._version}/chat/completions"
        async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(url, json=body) as response:
                    async for line in response.content:
                        yield line

    async def _embeddings_async(self, text, user=None):
        # check if text is a list of dicts
        if isinstance(text, list):
            if not isinstance(text[0], dict):
                raise ValueError("If text is a list, it must be a list of dicts with keys 'role' and 'content'.")
            else:
                # transform the dicts into a single string
                text = " ".join([str(message) for message in text])

        body = {
            "input": text,
            "model": self._embeddings_model,
        }
        if user:
            body["user"] = user
        url = f"{self._host}/{self._version}/embeddings"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(url, json=body) as response:
                return await response.json()
                    
    def embeddings(self, text: Union[str, List[dict]], user: Optional[str]=None):
        return asyncio.run(self._embeddings_async(text, user))