from dotenv import load_dotenv
import os
from typing import Any, Dict, Optional
from ..exceptions import APIKeyNotFoundError, UnsupportedOpenAIModelError

from langchain.chat_models import AzureChatOpenAI

from ..prompts.base import Prompt
from langchain.llms import AzureOpenAI
from .base import BaseOpenAI
from ..langchain import LangChain



load_dotenv()


class Model(BaseOpenAI):


    """AzureOpenAI LLM using BaseOpenAI Class.

    model_name: str  # gpt-35-turbo-16k  gpt-35-turbo
    api_version: str  # 2023-03-15-preview  2023-05-15
    deployment_name: str  # gpt-35-16k GPT35

    """

    api_token: str
    api_base:str
    model_name: str  
    api_version: str  
    max_tokens: int = 4097
    deployment_name: str  
    llm: AzureOpenAI
    
    _supported_chat_models = [
        "gpt-4",
        "gpt-4-0314",
        "gpt-4-32k",
        "gpt-4-32k-0314",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0301",
    ]
    _supported_completion_models = ["text-davinci-003"]

    model: str = "gpt-3.5-turbo"
    langchain: LangChain

    def __init__(self,
        api_token: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: str = None,
        model_name: str = None,
        **kwargs, ):

        self.api_token = api_token or os.getenv("AZURE_OPENAI_KEY") or None
        self.api_base = api_base or os.getenv("AZURE_OPENAI_ENDPOINT") or None
        self.api_version = api_version or os.getenv("AZURE_OPENAI_VERSION") or None
        self.deployment_name = deployment_name or os.getenv("DEPLOYMENT_NAME") or None
        self.model_name = model_name or os.getenv("MODEL_NAME") or None

        if self.api_token is None:
            raise APIKeyNotFoundError("Azure OpenAI key is required")
        if self.api_base is None:
            raise APIKeyNotFoundError("Azure OpenAI base endpoint is required")
        if self.deployment_name is None:
            raise UnsupportedOpenAIModelError("Model deployment name is required.")
        if self.model_name is None:
            raise UnsupportedOpenAIModelError("Model name is required.")
        if self.api_version is None:
            raise UnsupportedOpenAIModelError("Azure OpenAI version is required.")

        self.llm = AzureChatOpenAI(
            openai_api_base=self.api_base,
            openai_api_version=self.api_version,
            deployment_name=self.deployment_name,
            openai_api_key=self.api_token,
            openai_api_type="azure",
            max_tokens = self.max_tokens,
            model_name = self.model_name,
          )
        # print(self.llm)
        self.langchain = LangChain(llm = self.llm)
        self._set_params(**kwargs)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API"""
        return {
            **super()._default_params,
            "model": self.model,
        }

    def call(self, instruction: Prompt, value: str, suffix: str = "", history: list = None) -> str:
        """
        Call the OpenAI LLM.

        Args:
            instruction (Prompt): Instruction to pass
            value (str): Value to pass
            suffix (str): Suffix to pass

        Raises:
            UnsupportedOpenAIModelError: Unsupported model

        Returns:
            str: Response
        """
        self.last_prompt = str(instruction) + str(value)

        if self.model in self._supported_completion_models:
            response = self.completion(str(instruction) + str(value) + suffix)
        elif self.model in self._supported_chat_models:
            # response = self.chat_completion(str(instruction) + str(value) + suffix)
            response = self.langchain_input(str(instruction) + str(value) + suffix, history)
            # print(response)
        else:
            raise UnsupportedOpenAIModelError("Unsupported model")

        return response

    @property
    def type(self) -> str:
        return "openai"
        

