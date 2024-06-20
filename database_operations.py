"""
    This file contains the essential methods related to the used database like storing passages in chromadb.
"""

import string

from tqdm import tqdm
from document_processing import build_passages_objects, build_pdf_object_via_hyperlink, remove_empty_passages
from langchain_community.vectorstores import Chroma


def passages_storing(path_to_xl_file, chromadb_client, collection_name: string, records_limit=None,
                     embedding_function=None):
    """
      This function processes the passages_objects from a folder and stores them in a collection in the database.
      :param records_limit: number of records to be added to the database
      :param embedding_function: embedding function to be used (a list of embedding functions)
      :param chromadb_client: chromadb object
      :param path_to_xl_file: path to the Excel file containing the documents metadata (without titles)
      :param collection_name: name of the used collection within chromadb (a list of strings)
      :return: None
    """
    embedding_model_1 = embedding_function[0]
    embedding_model_2 = embedding_function[1]

    collection_with_concat = chromadb_client.get_or_create_collection(
        name=collection_name[1],
        embedding_function=embedding_model_2,
        metadata={"hnsw:space": "cosine"}
    )

    pdf_objects = build_pdf_object_via_hyperlink(path_to_xl_file, limit=records_limit)
    passages_objects = []

    print(f'building passages_objects ...\n')
    for pdf_object in tqdm(pdf_objects):
        french_passages_objects, dutch_passages_objects, _, _ = build_passages_objects(pdf_object)
        passages_objects.extend(french_passages_objects)
        passages_objects.extend(dutch_passages_objects)

    # remove empty passages
    filtered_passages = remove_empty_passages(passages_objects)

    print(f'\nComputing Dense Vectors for each passages .....')
    for i, passage_object in enumerate(tqdm(filtered_passages)):
        text_2_store = passage_object.metadata['passage_title'] + ' ' + passage_object.page_content
        passage_embedding = embedding_model_2.embed_query(text_2_store)
        try:
            Chroma.from_documents(
                [passage_object],
                embedding_model_1,
                collection_name=collection_name[0],
                client=chromadb_client,
                collection_metadata={"hnsw:space": "cosine"}
            )

            collection_with_concat.add(
                ids=str(i),
                documents=passage_object.page_content,
                embeddings=passage_embedding,
                metadatas=passage_object.metadata
            )

        except Exception as e:
            print(f'Error: {e}')

