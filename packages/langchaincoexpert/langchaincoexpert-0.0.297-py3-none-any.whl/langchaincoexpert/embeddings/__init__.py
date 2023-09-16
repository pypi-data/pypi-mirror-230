"""**Embedding models**  are wrappers around embedding models
from different APIs and services.

**Embedding models** can be LLMs or not.

**Class hierarchy:**

.. code-block::

    Embeddings --> <name>Embeddings  # Examples: OpenAIEmbeddings, HuggingFaceEmbeddings
"""


import logging
from typing import Any

from langchaincoexpert.embeddings.aleph_alpha import (
    AlephAlphaAsymmetricSemanticEmbedding,
    AlephAlphaSymmetricSemanticEmbedding,
)
from langchaincoexpert.embeddings.awa import AwaEmbeddings
from langchaincoexpert.embeddings.baidu_qianfan_endpoint import QianfanEmbeddingsEndpoint
from langchaincoexpert.embeddings.bedrock import BedrockEmbeddings
from langchaincoexpert.embeddings.cache import CacheBackedEmbeddings
from langchaincoexpert.embeddings.clarifai import ClarifaiEmbeddings
from langchaincoexpert.embeddings.cohere import CohereEmbeddings
from langchaincoexpert.embeddings.dashscope import DashScopeEmbeddings
from langchaincoexpert.embeddings.deepinfra import DeepInfraEmbeddings
from langchaincoexpert.embeddings.edenai import EdenAiEmbeddings
from langchaincoexpert.embeddings.elasticsearch import ElasticsearchEmbeddings
from langchaincoexpert.embeddings.embaas import EmbaasEmbeddings
from langchaincoexpert.embeddings.ernie import ErnieEmbeddings
from langchaincoexpert.embeddings.fake import DeterministicFakeEmbedding, FakeEmbeddings
from langchaincoexpert.embeddings.google_palm import GooglePalmEmbeddings
from langchaincoexpert.embeddings.gpt4all import GPT4AllEmbeddings
from langchaincoexpert.embeddings.huggingface import (
    HuggingFaceBgeEmbeddings,
    HuggingFaceEmbeddings,
    HuggingFaceInferenceAPIEmbeddings,
    HuggingFaceInstructEmbeddings,
)
from langchaincoexpert.embeddings.huggingface_hub import HuggingFaceHubEmbeddings
from langchaincoexpert.embeddings.jina import JinaEmbeddings
from langchaincoexpert.embeddings.llamacpp import LlamaCppEmbeddings
from langchaincoexpert.embeddings.localai import LocalAIEmbeddings
from langchaincoexpert.embeddings.minimax import MiniMaxEmbeddings
from langchaincoexpert.embeddings.mlflow_gateway import MlflowAIGatewayEmbeddings
from langchaincoexpert.embeddings.modelscope_hub import ModelScopeEmbeddings
from langchaincoexpert.embeddings.mosaicml import MosaicMLInstructorEmbeddings
from langchaincoexpert.embeddings.nlpcloud import NLPCloudEmbeddings
from langchaincoexpert.embeddings.octoai_embeddings import OctoAIEmbeddings
from langchaincoexpert.embeddings.ollama import OllamaEmbeddings
from langchaincoexpert.embeddings.openai import OpenAIEmbeddings
from langchaincoexpert.embeddings.sagemaker_endpoint import SagemakerEndpointEmbeddings
from langchaincoexpert.embeddings.self_hosted import SelfHostedEmbeddings
from langchaincoexpert.embeddings.self_hosted_hugging_face import (
    SelfHostedHuggingFaceEmbeddings,
    SelfHostedHuggingFaceInstructEmbeddings,
)
from langchaincoexpert.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchaincoexpert.embeddings.spacy_embeddings import SpacyEmbeddings
from langchaincoexpert.embeddings.tensorflow_hub import TensorflowHubEmbeddings
from langchaincoexpert.embeddings.vertexai import VertexAIEmbeddings
from langchaincoexpert.embeddings.xinference import XinferenceEmbeddings

logger = logging.getLogger(__name__)

__all__ = [
    "OpenAIEmbeddings",
    "CacheBackedEmbeddings",
    "ClarifaiEmbeddings",
    "CohereEmbeddings",
    "ElasticsearchEmbeddings",
    "HuggingFaceEmbeddings",
    "HuggingFaceInferenceAPIEmbeddings",
    "JinaEmbeddings",
    "LlamaCppEmbeddings",
    "HuggingFaceHubEmbeddings",
    "MlflowAIGatewayEmbeddings",
    "ModelScopeEmbeddings",
    "TensorflowHubEmbeddings",
    "SagemakerEndpointEmbeddings",
    "HuggingFaceInstructEmbeddings",
    "MosaicMLInstructorEmbeddings",
    "SelfHostedEmbeddings",
    "SelfHostedHuggingFaceEmbeddings",
    "SelfHostedHuggingFaceInstructEmbeddings",
    "FakeEmbeddings",
    "DeterministicFakeEmbedding",
    "AlephAlphaAsymmetricSemanticEmbedding",
    "AlephAlphaSymmetricSemanticEmbedding",
    "SentenceTransformerEmbeddings",
    "GooglePalmEmbeddings",
    "MiniMaxEmbeddings",
    "VertexAIEmbeddings",
    "BedrockEmbeddings",
    "DeepInfraEmbeddings",
    "EdenAiEmbeddings",
    "DashScopeEmbeddings",
    "EmbaasEmbeddings",
    "OctoAIEmbeddings",
    "SpacyEmbeddings",
    "NLPCloudEmbeddings",
    "GPT4AllEmbeddings",
    "XinferenceEmbeddings",
    "LocalAIEmbeddings",
    "AwaEmbeddings",
    "HuggingFaceBgeEmbeddings",
    "ErnieEmbeddings",
    "OllamaEmbeddings",
    "QianfanEmbeddingsEndpoint",
]


# TODO: this is in here to maintain backwards compatibility
class HypotheticalDocumentEmbedder:
    def __init__(self, *args: Any, **kwargs: Any):
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchaincoexpert.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchaincoexpert.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H(*args, **kwargs)  # type: ignore

    @classmethod
    def from_llm(cls, *args: Any, **kwargs: Any) -> Any:
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchaincoexpert.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchaincoexpert.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H.from_llm(*args, **kwargs)
