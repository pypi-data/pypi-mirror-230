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

class OpenAIInferenceClientTests:

    def test_generate_async_with_streaming(self):
        client = OpenAIInferenceClient("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", model="gpt-4")
        prompt = [{"role": "user", "content": "Once upon a time"}]
        temperature = 0.5
        top_p = 1.0
        n = 1
        presence_penalty = 0.0
        frequency_penalty = 0.0
        async def test():
            async for line in client.generate_stream(prompt, temperature=temperature, top_p=top_p, n=n,
                                                presence_penalty=presence_penalty, frequency_penalty=frequency_penalty):
                print(line)
        asyncio.run(test())

if __name__ == "__main__":
    OpenAIInferenceClientTests().test_generate_async_with_streaming()
    print("Done!")