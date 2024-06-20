"""
    This file contains two classes which define two custom embedding functions
"""

from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings

class CustomHuggingFaceEmbeddings(HuggingFaceEmbeddings):
    def __call__(self, input: str) -> list[float]:
        model_name = "all-MiniLM-L6-v2"
        model_kwargs = {'device': 'cpu'}
        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
        )
        return self.model.embed_query(input)


class CustomHuggingFaceBgeEmbeddings(HuggingFaceBgeEmbeddings):
    def __call__(self, input: str) -> list[float]:
        self.model = HuggingFaceBgeEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={"device": "cpu"},
            query_instruction="Represent the query for passage retrieval: "
        )
        return self.model.embed_query(input)

