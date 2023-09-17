"""**Chat Models** are a variation on language models.

While Chat Models use language models under the hood, the interface they expose
is a bit different. Rather than expose a "text in, text out" API, they expose
an interface where "chat messages" are the inputs and outputs.

**Class hierarchy:**

.. code-block::

    BaseLanguageModel --> BaseChatModel --> <name>  # Examples: ChatOpenAI, ChatGooglePalm

**Main helpers:**

.. code-block::

    AIMessage, BaseMessage, HumanMessage
"""  # noqa: E501

from langchaincoexpert.chat_models.anthropic import ChatAnthropic
from langchaincoexpert.chat_models.anyscale import ChatAnyscale
from langchaincoexpert.chat_models.azure_openai import AzureChatOpenAI
from langchaincoexpert.chat_models.baidu_qianfan_endpoint import QianfanChatEndpoint
from langchaincoexpert.chat_models.bedrock import BedrockChat
from langchaincoexpert.chat_models.ernie import ErnieBotChat
from langchaincoexpert.chat_models.fake import FakeListChatModel
from langchaincoexpert.chat_models.google_palm import ChatGooglePalm
from langchaincoexpert.chat_models.human import HumanInputChatModel
from langchaincoexpert.chat_models.jinachat import JinaChat
from langchaincoexpert.chat_models.konko import ChatKonko
from langchaincoexpert.chat_models.litellm import ChatLiteLLM
from langchaincoexpert.chat_models.mlflow_ai_gateway import ChatMLflowAIGateway
from langchaincoexpert.chat_models.ollama import ChatOllama
from langchaincoexpert.chat_models.openai import ChatOpenAI
from langchaincoexpert.chat_models.promptlayer_openai import PromptLayerChatOpenAI
from langchaincoexpert.chat_models.vertexai import ChatVertexAI

__all__ = [
    "ChatOpenAI",
    "BedrockChat",
    "AzureChatOpenAI",
    "FakeListChatModel",
    "PromptLayerChatOpenAI",
    "ChatAnthropic",
    "ChatGooglePalm",
    "ChatMLflowAIGateway",
    "ChatOllama",
    "ChatVertexAI",
    "JinaChat",
    "HumanInputChatModel",
    "ChatAnyscale",
    "ChatLiteLLM",
    "ErnieBotChat",
    "ChatKonko",
    "QianfanChatEndpoint",
]
