import string
from tqdm import tqdm
from document_processing import build_passages_objects, build_pdf_object_via_hyperlink, remove_empty_passages
from vector_database_manager import ChromaClient
import nltk

'''
This file contains the functions used to store the passages_objects in the database and to query the database
'''

#TODO: filter passages (remove those without text (only title)) from 57000 to 48000
def passages_storing(path_to_xl_file, chromadb_client: ChromaClient, collection_name:string, records_limit=None,
                     embedding_function=None):
    """
    This function processes the passages_objects from a folder and stores them in a collection in the database.
    :param records_limit: number of records to be added to the database
    :param embedding_function: embedding function to be used
    :param chromadb_client: ChromaClient object
    :param path_to_xl_file: path to the Excel file containing the metadata
    :param collection_name: name of the collection (SVD_for_documents_retrieval)
    :return: None
    """
    pdf_objects = build_pdf_object_via_hyperlink(path_to_xl_file, limit=records_limit)
    passages_objects = []

    print(f'building passages_objects ...\n')
    for pdf_object in tqdm(pdf_objects):
        french_passages_objects, dutch_passages_objects, _, _ = build_passages_objects(pdf_object)
        passages_objects.extend(french_passages_objects)
        passages_objects.extend(dutch_passages_objects)

    # remove empty passages
    filtered_passages = remove_empty_passages(passages_objects)
    print(len(filtered_passages))
    # load the collection
    main_collection = chromadb_client.get_collection(collection_name)

    # get the number of records in the collection
    collection_size = main_collection.count()

    passages_to_add = []
    embeddings_to_add = []
    metadata_to_add = []
    ids_to_add = []
    limit = collection_size + len(filtered_passages)
    #ids_to_add = [str(i) for i in range(collection_size, limit)]
    print(f'\nComputing Dense Vectors for each passages .....')
    for i, passage_object in enumerate(tqdm(filtered_passages)) :
        # store title + text
        text_2_store = passage_object.metadata['passage_title'] + ' ' + passage_object.passage_text
        passage_embedding = embedding_function(text_2_store)
        """ids_to_add.append(str(i))
        passages_to_add.append(passage_object.passage_text)
        embeddings_to_add.append(passage_embedding)
        metadata_to_add.append(passage_object.metadata)"""
        try:
            main_collection.add(ids=str(i),
                                documents=passage_object.passage_text,
                                embeddings=passage_embedding,
                                metadatas=passage_object.metadata
                                )
        except Exception as e:
            print(f'Error: {e}')
            print(f'Only {len(passages_to_add)} passages_objects were added to the collection {collection_name}')

    print(f'{len(passages_to_add)} passages_objects were added to the collection {collection_name}')
