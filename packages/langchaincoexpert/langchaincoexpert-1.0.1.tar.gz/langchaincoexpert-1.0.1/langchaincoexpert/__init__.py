# ruff: noqa: E402
"""Main entrypoint into package."""
from importlib import metadata
from typing import Optional

from langchaincoexpert.agents import MRKLChain, ReActChain, SelfAskWithSearchChain
from langchaincoexpert.chains import (
    ConversationChain,
    LLMBashChain,
    LLMChain,
    LLMCheckerChain,
    LLMMathChain,
    QAWithSourcesChain,
    VectorDBQA,
    VectorDBQAWithSourcesChain,
)
from langchaincoexpert.docstore import InMemoryDocstore, Wikipedia
from langchaincoexpert.llms import (
    Anthropic,
    Banana,
    CerebriumAI,
    Cohere,
    ForefrontAI,
    GooseAI,
    HuggingFaceHub,
    HuggingFaceTextGenInference,
    LlamaCpp,
    Modal,
    OpenAI,
    Petals,
    PipelineAI,
    SagemakerEndpoint,
    StochasticAI,
    Writer,
)
from langchaincoexpert.llms.huggingface_pipeline import HuggingFacePipeline
from langchaincoexpert.prompts import (
    FewShotPromptTemplate,
    Prompt,
    PromptTemplate,
)
from langchaincoexpert.schema.cache import BaseCache
from langchaincoexpert.schema.prompt_template import BasePromptTemplate
from langchaincoexpert.utilities.arxiv import ArxivAPIWrapper
from langchaincoexpert.utilities.golden_query import GoldenQueryAPIWrapper
from langchaincoexpert.utilities.google_search import GoogleSearchAPIWrapper
from langchaincoexpert.utilities.google_serper import GoogleSerperAPIWrapper
from langchaincoexpert.utilities.powerbi import PowerBIDataset
from langchaincoexpert.utilities.searx_search import SearxSearchWrapper
from langchaincoexpert.utilities.serpapi import SerpAPIWrapper
from langchaincoexpert.utilities.sql_database import SQLDatabase
from langchaincoexpert.utilities.wikipedia import WikipediaAPIWrapper
from langchaincoexpert.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchaincoexpert.vectorstores import FAISS, ElasticVectorSearch

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

verbose: bool = False
debug: bool = False
llm_cache: Optional[BaseCache] = None

# For backwards compatibility
SerpAPIChain = SerpAPIWrapper


__all__ = [
    "LLMChain",
    "LLMBashChain",
    "LLMCheckerChain",
    "LLMMathChain",
    "ArxivAPIWrapper",
    "GoldenQueryAPIWrapper",
    "SelfAskWithSearchChain",
    "SerpAPIWrapper",
    "SerpAPIChain",
    "SearxSearchWrapper",
    "GoogleSearchAPIWrapper",
    "GoogleSerperAPIWrapper",
    "WolframAlphaAPIWrapper",
    "WikipediaAPIWrapper",
    "Anthropic",
    "Banana",
    "CerebriumAI",
    "Cohere",
    "ForefrontAI",
    "GooseAI",
    "Modal",
    "OpenAI",
    "Petals",
    "PipelineAI",
    "StochasticAI",
    "Writer",
    "BasePromptTemplate",
    "Prompt",
    "FewShotPromptTemplate",
    "PromptTemplate",
    "ReActChain",
    "Wikipedia",
    "HuggingFaceHub",
    "SagemakerEndpoint",
    "HuggingFacePipeline",
    "SQLDatabase",
    "PowerBIDataset",
    "FAISS",
    "MRKLChain",
    "VectorDBQA",
    "ElasticVectorSearch",
    "InMemoryDocstore",
    "ConversationChain",
    "VectorDBQAWithSourcesChain",
    "QAWithSourcesChain",
    "LlamaCpp",
    "HuggingFaceTextGenInference",
]
