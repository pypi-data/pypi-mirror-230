# ruff: noqa: E402
"""Main entrypoint into package."""
from importlib import metadata
from typing import Optional

from langchainn.agents import MRKLChain, ReActChain, SelfAskWithSearchChain
from langchainn.chains import (
    ConversationChain,
    LLMBashChain,
    LLMChain,
    LLMCheckerChain,
    LLMMathChain,
    QAWithSourcesChain,
    VectorDBQA,
    VectorDBQAWithSourcesChain,
)
from langchainn.docstore import InMemoryDocstore, Wikipedia
from langchainn.llms import (
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
from langchainn.llms.huggingface_pipeline import HuggingFacePipeline
from langchainn.prompts import (
    FewShotPromptTemplate,
    Prompt,
    PromptTemplate,
)
from langchainn.schema.cache import BaseCache
from langchainn.schema.prompt_template import BasePromptTemplate
from langchainn.utilities.arxiv import ArxivAPIWrapper
from langchainn.utilities.golden_query import GoldenQueryAPIWrapper
from langchainn.utilities.google_search import GoogleSearchAPIWrapper
from langchainn.utilities.google_serper import GoogleSerperAPIWrapper
from langchainn.utilities.powerbi import PowerBIDataset
from langchainn.utilities.searx_search import SearxSearchWrapper
from langchainn.utilities.serpapi import SerpAPIWrapper
from langchainn.utilities.sql_database import SQLDatabase
from langchainn.utilities.wikipedia import WikipediaAPIWrapper
from langchainn.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchainn.vectorstores import FAISS, ElasticVectorSearch

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
