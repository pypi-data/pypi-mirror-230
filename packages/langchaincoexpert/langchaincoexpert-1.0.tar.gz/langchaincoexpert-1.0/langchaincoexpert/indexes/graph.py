"""Graph Index Creator."""
from typing import Optional, Type

from langchaincoexpert import BasePromptTemplate
from langchaincoexpert.chains.llm import LLMChain
from langchaincoexpert.graphs.networkx_graph import NetworkxEntityGraph, parse_triples
from langchaincoexpert.indexes.prompts.knowledge_triplet_extraction import (
    KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT,
)
from langchaincoexpert.pydantic_v1 import BaseModel
from langchaincoexpert.schema.language_model import BaseLanguageModel


class GraphIndexCreator(BaseModel):
    """Functionality to create graph index."""

    llm: Optional[BaseLanguageModel] = None
    graph_type: Type[NetworkxEntityGraph] = NetworkxEntityGraph

    def from_text(
        self, text: str, prompt: BasePromptTemplate = KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT
    ) -> NetworkxEntityGraph:
        """Create graph index from text."""
        if self.llm is None:
            raise ValueError("llm should not be None")
        graph = self.graph_type()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        output = chain.predict(text=text)
        knowledge = parse_triples(output)
        for triple in knowledge:
            graph.add_triple(triple)
        return graph

    async def afrom_text(
        self, text: str, prompt: BasePromptTemplate = KNOWLEDGE_TRIPLE_EXTRACTION_PROMPT
    ) -> NetworkxEntityGraph:
        """Create graph index from text asynchronously."""
        if self.llm is None:
            raise ValueError("llm should not be None")
        graph = self.graph_type()
        chain = LLMChain(llm=self.llm, prompt=prompt)
        output = await chain.apredict(text=text)
        knowledge = parse_triples(output)
        for triple in knowledge:
            graph.add_triple(triple)
        return graph
