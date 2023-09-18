"""
**LLM** classes provide
access to the large language model (**LLM**) APIs and services.

**Class hierarchy:**

.. code-block::

    BaseLanguageModel --> BaseLLM --> LLM --> <name>  # Examples: AI21, HuggingFaceHub, OpenAI

**Main helpers:**

.. code-block::

    LLMResult, PromptValue,
    CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun,
    CallbackManager, AsyncCallbackManager,
    AIMessage, BaseMessage
"""  # noqa: E501
from typing import Dict, Type

from langchaincoexpert.llms.ai21 import AI21
from langchaincoexpert.llms.aleph_alpha import AlephAlpha
from langchaincoexpert.llms.amazon_api_gateway import AmazonAPIGateway
from langchaincoexpert.llms.anthropic import Anthropic
from langchaincoexpert.llms.anyscale import Anyscale
from langchaincoexpert.llms.aviary import Aviary
from langchaincoexpert.llms.azureml_endpoint import AzureMLOnlineEndpoint
from langchaincoexpert.llms.baidu_qianfan_endpoint import QianfanLLMEndpoint
from langchaincoexpert.llms.bananadev import Banana
from langchaincoexpert.llms.base import BaseLLM
from langchaincoexpert.llms.baseten import Baseten
from langchaincoexpert.llms.beam import Beam
from langchaincoexpert.llms.bedrock import Bedrock
from langchaincoexpert.llms.bittensor import NIBittensorLLM
from langchaincoexpert.llms.cerebriumai import CerebriumAI
from langchaincoexpert.llms.chatglm import ChatGLM
from langchaincoexpert.llms.clarifai import Clarifai
from langchaincoexpert.llms.cohere import Cohere
from langchaincoexpert.llms.ctransformers import CTransformers
from langchaincoexpert.llms.ctranslate2 import CTranslate2
from langchaincoexpert.llms.databricks import Databricks
from langchaincoexpert.llms.deepinfra import DeepInfra
from langchaincoexpert.llms.deepsparse import DeepSparse
from langchaincoexpert.llms.edenai import EdenAI
from langchaincoexpert.llms.fake import FakeListLLM
from langchaincoexpert.llms.fireworks import Fireworks, FireworksChat
from langchaincoexpert.llms.forefrontai import ForefrontAI
from langchaincoexpert.llms.google_palm import GooglePalm
from langchaincoexpert.llms.gooseai import GooseAI
from langchaincoexpert.llms.gpt4all import GPT4All
from langchaincoexpert.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchaincoexpert.llms.huggingface_hub import HuggingFaceHub
from langchaincoexpert.llms.huggingface_pipeline import HuggingFacePipeline
from langchaincoexpert.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchaincoexpert.llms.human import HumanInputLLM
from langchaincoexpert.llms.koboldai import KoboldApiLLM
from langchaincoexpert.llms.llamacpp import LlamaCpp
from langchaincoexpert.llms.manifest import ManifestWrapper
from langchaincoexpert.llms.minimax import Minimax
from langchaincoexpert.llms.mlflow_ai_gateway import MlflowAIGateway
from langchaincoexpert.llms.modal import Modal
from langchaincoexpert.llms.mosaicml import MosaicML
from langchaincoexpert.llms.nlpcloud import NLPCloud
from langchaincoexpert.llms.octoai_endpoint import OctoAIEndpoint
from langchaincoexpert.llms.ollama import Ollama
from langchaincoexpert.llms.opaqueprompts import OpaquePrompts
from langchaincoexpert.llms.openai import AzureOpenAI, OpenAI, OpenAIChat
from langchaincoexpert.llms.openllm import OpenLLM
from langchaincoexpert.llms.openlm import OpenLM
from langchaincoexpert.llms.petals import Petals
from langchaincoexpert.llms.pipelineai import PipelineAI
from langchaincoexpert.llms.predibase import Predibase
from langchaincoexpert.llms.predictionguard import PredictionGuard
from langchaincoexpert.llms.promptlayer_openai import PromptLayerOpenAI, PromptLayerOpenAIChat
from langchaincoexpert.llms.replicate import Replicate
from langchaincoexpert.llms.rwkv import RWKV
from langchaincoexpert.llms.sagemaker_endpoint import SagemakerEndpoint
from langchaincoexpert.llms.self_hosted import SelfHostedPipeline
from langchaincoexpert.llms.self_hosted_hugging_face import SelfHostedHuggingFaceLLM
from langchaincoexpert.llms.stochasticai import StochasticAI
from langchaincoexpert.llms.symblai_nebula import Nebula
from langchaincoexpert.llms.textgen import TextGen
from langchaincoexpert.llms.titan_takeoff import TitanTakeoff
from langchaincoexpert.llms.tongyi import Tongyi
from langchaincoexpert.llms.vertexai import VertexAI, VertexAIModelGarden
from langchaincoexpert.llms.vllm import VLLM, VLLMOpenAI
from langchaincoexpert.llms.writer import Writer
from langchaincoexpert.llms.xinference import Xinference

__all__ = [
    "AI21",
    "AlephAlpha",
    "AmazonAPIGateway",
    "Anthropic",
    "Anyscale",
    "Aviary",
    "AzureMLOnlineEndpoint",
    "AzureOpenAI",
    "Banana",
    "Baseten",
    "Beam",
    "Bedrock",
    "CTransformers",
    "CTranslate2",
    "CerebriumAI",
    "ChatGLM",
    "Clarifai",
    "Cohere",
    "Databricks",
    "DeepInfra",
    "DeepSparse",
    "EdenAI",
    "FakeListLLM",
    "Fireworks",
    "FireworksChat",
    "ForefrontAI",
    "GPT4All",
    "GooglePalm",
    "GooseAI",
    "HuggingFaceEndpoint",
    "HuggingFaceHub",
    "HuggingFacePipeline",
    "HuggingFaceTextGenInference",
    "HumanInputLLM",
    "KoboldApiLLM",
    "LlamaCpp",
    "TextGen",
    "ManifestWrapper",
    "Minimax",
    "MlflowAIGateway",
    "Modal",
    "MosaicML",
    "Nebula",
    "NIBittensorLLM",
    "NLPCloud",
    "Ollama",
    "OpenAI",
    "OpenAIChat",
    "OpenLLM",
    "OpenLM",
    "Petals",
    "PipelineAI",
    "Predibase",
    "PredictionGuard",
    "PromptLayerOpenAI",
    "PromptLayerOpenAIChat",
    "OpaquePrompts",
    "RWKV",
    "Replicate",
    "SagemakerEndpoint",
    "SelfHostedHuggingFaceLLM",
    "SelfHostedPipeline",
    "StochasticAI",
    "TitanTakeoff",
    "Tongyi",
    "VertexAI",
    "VertexAIModelGarden",
    "VLLM",
    "VLLMOpenAI",
    "Writer",
    "OctoAIEndpoint",
    "Xinference",
    "QianfanLLMEndpoint",
]

type_to_cls_dict: Dict[str, Type[BaseLLM]] = {
    "ai21": AI21,
    "aleph_alpha": AlephAlpha,
    "amazon_api_gateway": AmazonAPIGateway,
    "amazon_bedrock": Bedrock,
    "anthropic": Anthropic,
    "anyscale": Anyscale,
    "aviary": Aviary,
    "azure": AzureOpenAI,
    "azureml_endpoint": AzureMLOnlineEndpoint,
    "bananadev": Banana,
    "baseten": Baseten,
    "beam": Beam,
    "cerebriumai": CerebriumAI,
    "chat_glm": ChatGLM,
    "clarifai": Clarifai,
    "cohere": Cohere,
    "ctransformers": CTransformers,
    "ctranslate2": CTranslate2,
    "databricks": Databricks,
    "deepinfra": DeepInfra,
    "deepsparse": DeepSparse,
    "edenai": EdenAI,
    "fake-list": FakeListLLM,
    "forefrontai": ForefrontAI,
    "google_palm": GooglePalm,
    "gooseai": GooseAI,
    "gpt4all": GPT4All,
    "huggingface_endpoint": HuggingFaceEndpoint,
    "huggingface_hub": HuggingFaceHub,
    "huggingface_pipeline": HuggingFacePipeline,
    "huggingface_textgen_inference": HuggingFaceTextGenInference,
    "human-input": HumanInputLLM,
    "koboldai": KoboldApiLLM,
    "llamacpp": LlamaCpp,
    "textgen": TextGen,
    "minimax": Minimax,
    "mlflow-ai-gateway": MlflowAIGateway,
    "modal": Modal,
    "mosaic": MosaicML,
    "nebula": Nebula,
    "nibittensor": NIBittensorLLM,
    "nlpcloud": NLPCloud,
    "ollama": Ollama,
    "openai": OpenAI,
    "openlm": OpenLM,
    "petals": Petals,
    "pipelineai": PipelineAI,
    "predibase": Predibase,
    "opaqueprompts": OpaquePrompts,
    "replicate": Replicate,
    "rwkv": RWKV,
    "sagemaker_endpoint": SagemakerEndpoint,
    "self_hosted": SelfHostedPipeline,
    "self_hosted_hugging_face": SelfHostedHuggingFaceLLM,
    "stochasticai": StochasticAI,
    "tongyi": Tongyi,
    "titan_takeoff": TitanTakeoff,
    "vertexai": VertexAI,
    "vertexai_model_garden": VertexAIModelGarden,
    "openllm": OpenLLM,
    "openllm_client": OpenLLM,
    "vllm": VLLM,
    "vllm_openai": VLLMOpenAI,
    "writer": Writer,
    "xinference": Xinference,
    "qianfan_endpoint": QianfanLLMEndpoint,
}
