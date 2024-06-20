"""
    This file contains the essential methods which can be used to manipulate chromadb objects and dates format.
"""

import chromadb
from datetime import datetime


def reset(chroma_client: chromadb):
    """
        Empties and completely resets the database. ⚠️ This is destructive and not reversible
        :param chroma_client: a chromadb object
        :return: a reset operation on the database
    """
    return chroma_client.reset()


def count_elem_in_collection(chroma_client: chromadb, collection_name: str):
    """
        Counts elements in the collection named <collection_name> within a chroma database initialised with <chroma_client>
        :param chroma_client: a chromadb object
        :param collection_name: the collection's name
        :return: Number of elements in that particular collection (named <collection_name>)
    """
    return chroma_client.get_or_create_collection(name=collection_name).count()


def delete_elem_in_collection(chroma_client: chromadb, collection_name: str):
    """
        Deletes elements in the collection named <collection_name> within a chroma database initialised with <chroma_client>
        :param chroma_client: a chromadb object
        :param collection_name: the collection's name
        :return: an empty collection named <collection_name>
    """
    return chroma_client.delete_collection(collection_name)


def get_create_collection(chroma_client: chromadb, collection_name: str, embedding=None):
    """
        Gets or creates a new collection <collecion_name> with or without specifying an embedding function <embeddning>
        :param chroma_client: a chromadb object
        :param collection_name: the collection's name
        :param embedding: embedding function to be used.
        :return: a newly created chromadb collection <collection_name> or an existing one <collection_name> if it is already created
    """
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
    """
        Takes a date <date> as input and format it in a particulat format : < %Y-%m-%d %H:%M:%S >
        :param date: a date to be processed
        :return: same date in the given format < %Y-%m-%d %H:%M:%S >
    """
    date_format = '%Y-%m-%d %H:%M:%S'
    return ((datetime.strptime(date, date_format)).date()).strftime("%d/%m/%Y")
