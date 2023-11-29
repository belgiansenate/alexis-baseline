from enum import Enum
from typing import List
import chromadb
from passage_object import PassageObject


class Mode(Enum):
    host = 'host'
    local = 'local'


class ChromaClient:
    def __init__(self, path_directory=None, host=None, port_number=None, mode: Mode = Mode.local,
                 embedding_function=None):

        if mode == Mode.host:
            self.chroma_client = chromadb.HttpClient(host=host, port=port_number)
        elif mode == Mode.local:
            self.chroma_client = chromadb.PersistentClient(path=path_directory)
        self.embedding_function = embedding_function

    def get_collection(self, name: str):
        if self.embedding_function is None:
            return self.chroma_client.get_collection(name=name)
        return self.chroma_client.get_collection(name=name, embedding_function=self.embedding_function)

    def delete_collection(self, name: str):
        return self.chroma_client.delete_collection(name=name)

    def reset(self):
        self.chroma_client.reset()

    def get_or_create_collection(self, collection_name):
        if self.embedding_function is None:
            return self.chroma_client.get_or_create_collection(name=collection_name)
        return self.chroma_client.get_or_create_collection(name=collection_name,
                                                           embedding_function=self.embedding_function)
