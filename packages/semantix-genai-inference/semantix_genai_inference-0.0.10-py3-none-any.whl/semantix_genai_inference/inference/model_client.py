import os
import yaml
from semantix_genai_inference.inference.llm.alpaca import AlpacaInferenceClient
from semantix_genai_inference.inference.llm.llama2 import Llama2InferenceClient
from semantix_genai_inference.inference.llm.cohere import CohereInferenceClient
from semantix_genai_inference.inference.llm.openai import OpenAIInferenceClient

class ModelClient:

    @staticmethod
    def create(client_type):
        """
        Create a client for a given model type and inference server id
        
        Args:
            client_type (str): The type of model client to create. Valid options are "alpaca", "llama2", "cohere"
        """
        config = ModelClient()._load_config()
        if client_type == "alpaca":
            semantix = config["providers"]["semantixHub"]
            inference_server_id = semantix["serverId"]
            api_secret = semantix["apiSecret"] if "apiSecret" in semantix else None
            version = semantix["version"]
            return AlpacaInferenceClient(inference_server_id, api_secret, version=version)
        elif client_type == "llama2":
            semantix = config["providers"]["semantixHub"]
            inference_server_id = semantix["serverId"]
            api_secret = semantix["apiSecret"] if "apiSecret" in semantix else None
            version = semantix["version"]
            return Llama2InferenceClient(inference_server_id, api_secret, version=version)
        elif client_type == "cohere":
            cohere = config["providers"]["cohere"]
            api_key = cohere["apiKey"] if "apiKey" in cohere else None
            generate_model = cohere["generate"]["model"]
            version = cohere["generate"]["version"]
            return CohereInferenceClient(api_key, generate_model, version=version)
        elif client_type == "openai":
            openai = config["providers"]["openai"]
            api_key = openai["apiKey"] if "apiKey" in openai else None
            model = openai["chat"]["model"]
            version = openai["chat"]["version"]
            return OpenAIInferenceClient(api_key, model, version=version)
        else:
            raise Exception(f"Invalid model client type: {client_type}")
    
    def _load_config(self):
        """
        Load the semantix.yaml file from the same directory where the application was executed
        """
        # check if SEMANTIX_CONFIG_FILE env exists otherwise use default
        config_file = "semantix.yaml"
        if "SEMANTIX_CONFIG_FILE" in os.environ:
            config_file = os.environ["SEMANTIX_CONFIG_FILE"]
        # check if file exists
        if not os.path.isfile(config_file):
            raise Exception(f"No {config_file} file found. The model client factory will not work, you may work instantiating the models directly.")
        with open(config_file) as f:
            config = yaml.safe_load(f)
        return config