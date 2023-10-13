from enum import Enum
from typing import Optional, Collection, List

import chromadb

from passage_object import PassageObject


class Mode(Enum):
    host = 'host'
    local = 'local'


class ChromaClient:
    def __init__(self, path_directory=None, host=None, port_number=None, mode: Mode = Mode.local):

        if mode == Mode.host:
            self.chroma_client = chromadb.HttpClient(host=host, port=port_number)
        elif mode == Mode.local:
            self.chroma_client = chromadb.PersistentClient(path=path_directory)

    def create_collection(self, name: str, embedding_function):
        return self.chroma_client.create_collection(name=name, embedding_function=embedding_function)

    def get_collection(self, name: str, embedding_function=None):
        if embedding_function is None:
            return self.chroma_client.get_collection(name=name)
        return self.chroma_client.get_collection(name=name, embedding_function=embedding_function)

    def delete_collection(self, name: str):
        return self.chroma_client.delete_collection(name=name)

    def store_documents(self, collection_name, chunks: List[PassageObject]):
        collection = self.chroma_client.get_collection(collection_name)
        collection.add(
            documents=[chunk.passage_text for chunk in chunks],
            metadatas=[chunk.document_id for chunk in chunks],
            ids=[chunk.passage_id for chunk in chunks]
        )

    def reset(self):
        self.chroma_client.reset()
