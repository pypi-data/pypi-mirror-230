import os
from typing import Optional, List, Union
from abc import ABC, abstractmethod

class SemantixGenClient(ABC):
    def __init__(self, inference_server_id: str, api_secret: Optional[str], 
                 version: Optional[str]="v0", server: Optional[str]="app.elemeno.ai"):
        self.inference_server_id = inference_server_id
        self.url = f"https://infserv-{inference_server_id}.{server}/{version}/inference"

        if not api_secret:
            api_secret = os.environ.get("SEMANTIX_API_SECRET")
        if not api_secret:
            raise Exception("No API secret provided. Either pass it as an argument or set the SEMANTIX_API_SECRET environment variable.")

        # set the Authorization header on aiohttp.ClientSession
        self.headers = {
            "Authorization": f"Bearer {api_secret}",
        }

    def add_header(self, key, value):
        self.headers[key] = value

    @abstractmethod
    def generate(self, **kwargs):
        pass

class CohereClient(ABC):

    def __init__(self, api_key: Optional[str]=None, 
                 generate_model: Optional[str] = "command",
                 version: Optional[str] = "v1"):
        self._api_key = api_key
        self._generate_model = generate_model
        self._host = "https://api.cohere.ai"
        self._version = version

        if not api_key:
            api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise Exception("No API key provided. Either pass it as an argument or set the COHERE_API_KEY environment variable.")

        # set the Authorization header on aiohttp.ClientSession
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }

    def add_header(self, key, value):
        self.headers[key] = value

    @abstractmethod
    def generate(self, prompt: str, num_generations: Optional[int],
                 stream: Optional[bool], max_tokens: Optional[int],
                 truncate: Optional[str], temperature: Optional[float],
                 preset: Optional[str], end_sequences: Optional[List[str]],
                 stop_sequences: Optional[List[str]], k: Optional[int], 
                 p: Optional[float], frequency_penalty: Optional[float],
                 presence_penalty: Optional[float], return_likelihoods: Optional[str],
                 logit_bias: Optional[dict]):
        """  Call cohere generate API to generates realistic text conditioned on a given input.

        Args:
            prompt (str): The input text that serves as the starting point for generating the response. Note: The prompt will be pre-processed and modified before reaching the model.
            num_generations (int, optional): The maximum number of generations that will be returned. Defaults to 1, min value of 1, max value of 5
            stream (bool, optional): When true, the response will be a JSON stream of events. Streaming is beneficial for user interfaces that render the contents of the response piece by piece, as it gets generated.
            max_tokens (int, optional): The maximum number of tokens the model will generate as part of the response. Note: Setting a low value may result in incomplete generations. Defaults to 20
            truncate (str, optional): One of NONE|START|END to specify how the API will handle inputs longer than the maximum token length.
            temperature (float, optional): A non-negative float that tunes the degree of randomness in generation. Lower temperatures mean less random generations. Defaults to 0.75, min value of 0.0, max value of 5.0.
            preset (str, optional): Identifier of a custom preset. A preset is a combination of parameters, such as prompt, temperature etc
            end_sequences (List[str], optional): The generated text will be cut at the beginning of the earliest occurence of an end sequence. The sequence will be excluded from the text
            start_sequences (List[str], optional): The generated text will be cut at the end of the earliest occurence of a stop sequence. The sequence will be included the text
            k (int, optional): Ensures only the top k most likely tokens are considered for generation at each step. Defaults to 0, min value of 0, max value of 500
            p (float, optional): Ensures that only the most likely tokens, with total probability mass of p, are considered for generation at each step. If both k and p are enabled, p acts after k. Defaults to 0. min value of 0.01, max value of 0.99
            frequency_penalty (float, optional): Used to reduce repetitiveness of generated tokens. The higher the value, the stronger a penalty is applied to previously present tokens, proportional to how many times they have already appeared in the prompt or prior generation
            presence_penalty (float, optional): Defaults to 0.0, min value of 0.0, max value of 1.0. Can be used to reduce repetitiveness of generated tokens. Similar to frequency_penalty, except that this penalty is applied equally to all tokens that have already appeared, regardless of their exact frequencies
            return_likelihoods (str, optional): One of GENERATION|ALL|NONE to specify how and if the token likelihoods are returned with the response. Defaults to NONE
            logit_bias (dict, optional): sed to prevent the model from generating unwanted tokens or to incentivize it to include desired tokens. The format is {token_id: bias} where bias is a float between -10 and 10
        """
        pass

class OpenAIClient(ABC):

    def __init__(self, api_key: Optional[str]=None, 
                 model: Optional[str] = "gpt-4",
                 embeddings_model: Optional[str] = "text-embedding-ada-002",
                 host: Optional[str] = "https://api.openai.com",
                 version: Optional[str] = "v1"):
        self._api_key = api_key
        self._model = model
        self._embeddings_model = embeddings_model
        self._host = host
        self._version = version

        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise Exception("No API key provided. Either pass it as an argument or set the COHERE_API_KEY environment variable.")

        # set the Authorization header on aiohttp.ClientSession
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }

    def add_header(self, key, value):
        self.headers[key] = value

    @abstractmethod
    def generate(self, messages: List[dict], functions: Optional[List[dict]], function_call: Optional[str],
                    temperature: Optional[float], top_p: Optional[float], n: Optional[int], stop: Optional[Union[str, List[str]]], 
                    max_tokens: Optional[int], presence_penalty: Optional[float], frequency_penalty: Optional[float], 
                    logit_bias: Optional[dict], user: Optional[str]
                 ):
        """  Call OpenAI API to create a chat completion for the provided prompt and parameters

        Args:
            messages (List[dict]): A list of messages comprising the conversation so far. Each message is a dictionary with the following keys: role, content, name, and function_call.
            functions (List[dict], optional): A list of functions the model may generate JSON inputs for. Each message is a dictionary with the following keys: name, description, and parameters.
            function_call (str, optional): Controls how the model responds to function calls. none means the model does not call a function, and responds to the end-user. auto means the model can pick between an end-user or calling a function. Specifying a particular function via {"name": "my_function"} forces the model to call that function. none is the default when no functions are present. auto is the default if functions are present.
            temperature (float, optional): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
            top_p (float, optional): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
            n (int, optional): How many chat completion choices to generate for each input message.
            logprobs (int, optional): Include the log probabilities on the logprobs most likely tokens, as well the chosen tokens. For example, if logprobs is 10, the API will return a list of the 10 most likely tokens.
            echo (bool, optional): Echo back the prompt in addition to the completion.
            stop (Union[str, List[str]], optional): One or more sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
            presence_penalty (float, optional): What penalty to apply if a token is already present at all. Between 0 and 1.
            frequency_penalty (float, optional): What penalty to apply if a token has already been generated. 0 means no penalty. Between 0 and 1.
            best_of (int, optional): Generates best_of completions server-side and returns the "best" (the one with the lowest log probability per token). Results cannot be streamed.
            logit_bias (dict, optional): Modify the likelihood of specified tokens appearing in the completion. Accepts a json object that maps tokens (specified by their token ID in the GPT tokenizer) to an associated bias value from -100 to 100. You can use this tokenizer tool (which works for both GPT-2 and GPT-3) to convert text to token IDs. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token.
            user (str, optional): A string to use as the user identifier for the request. This will let opeani correlate requests with your usage in the billing dashboard.
        """
        pass

    @abstractmethod
    async def generate_stream(self, messages: List[dict], functions: Optional[List[dict]], function_call: Optional[str],
                    temperature: Optional[float], top_p: Optional[float], n: Optional[int], stop: Optional[Union[str, List[str]]], 
                    max_tokens: Optional[int], presence_penalty: Optional[float], frequency_penalty: Optional[float], 
                    logit_bias: Optional[dict], user: Optional[str]
                 ):
        """  Call OpenAI API to create a chat completion for the provided prompt and parameters

        Args:
            messages (List[dict]): A list of messages comprising the conversation so far. Each message is a dictionary with the following keys: role, content, name, and function_call.
            functions (List[dict], optional): A list of functions the model may generate JSON inputs for. Each message is a dictionary with the following keys: name, description, and parameters.
            function_call (str, optional): Controls how the model responds to function calls. none means the model does not call a function, and responds to the end-user. auto means the model can pick between an end-user or calling a function. Specifying a particular function via {"name": "my_function"} forces the model to call that function. none is the default when no functions are present. auto is the default if functions are present.
            temperature (float, optional): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
            top_p (float, optional): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
            n (int, optional): How many chat completion choices to generate for each input message.
            logprobs (int, optional): Include the log probabilities on the logprobs most likely tokens, as well the chosen tokens. For example, if logprobs is 10, the API will return a list of the 10 most likely tokens.
            echo (bool, optional): Echo back the prompt in addition to the completion.
            stop (Union[str, List[str]], optional): One or more sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
            presence_penalty (float, optional): What penalty to apply if a token is already present at all. Between 0 and 1.
            frequency_penalty (float, optional): What penalty to apply if a token has already been generated. 0 means no penalty. Between 0 and 1.
            best_of (int, optional): Generates best_of completions server-side and returns the "best" (the one with the lowest log probability per token). Results cannot be streamed.
            logit_bias (dict, optional): Modify the likelihood of specified tokens appearing in the completion. Accepts a json object that maps tokens (specified by their token ID in the GPT tokenizer) to an associated bias value from -100 to 100. You can use this tokenizer tool (which works for both GPT-2 and GPT-3) to convert text to token IDs. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token.
            user (str, optional): A string to use as the user identifier for the request. This will let opeani correlate requests with your usage in the billing dashboard.
        """
        pass
    
    @abstractmethod
    def embeddings(self, text: Union[str, List[dict]], user: Optional[str]):
        """  Call OpenAI embedding API to tokenize the provided text

        Args:
            text (Union[str, List[dict]]): A string or a list of message objects to tokenize
            user (str, optional): A string to use as the user identifier for the request. This will let opeani correlate requests with your usage in the billing dashboard.

        Returns:
            List[dict]: A list of embedding objects
        """
        pass