import chromadb
from datetime import datetime


# Empties and completely resets the database. ⚠️ This is destructive and not reversible
def reset(chroma_client: chromadb):
    return chroma_client.reset()


def count_elem_in_collection(chroma_client: chromadb, collection_name: str):
    return chroma_client.get_or_create_collection(name=collection_name).count()


def delete_elem_in_collection(chroma_client: chromadb, collection_name: str):
    return chroma_client.delete_collection(collection_name)


def get_create_collection(chroma_client: chromadb, collection_name: str, embedding=None):
    if embedding is None:
        return chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    else:
        return chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding,
            metadata={"hnsw:space": "cosine"}
        )

def date_printing(date):
    date_format = '%Y-%m-%d %H:%M:%S'
    return ((datetime.strptime(date, date_format)).date()).strftime("%d/%m/%Y")
