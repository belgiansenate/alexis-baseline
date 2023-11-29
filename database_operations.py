import string
from tqdm import tqdm
from document_processing import build_passages_objects, build_pdf_object_via_hyperlink
from vector_database_manager import ChromaClient


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

    print(f'building passages_objects ...')
    for pdf_object in tqdm(pdf_objects):
        french_passages_objects, dutch_passages_objects, _, _ = build_passages_objects(pdf_object)
        passages_objects.extend(french_passages_objects)
        passages_objects.extend(dutch_passages_objects)

    main_collection = chromadb_client.get_collection(collection_name)
    collection_size = main_collection.count()

    passages_to_add = []
    embeddings_to_add = []
    metadata_to_add = []
    limit = collection_size + len(passages_objects)
    ids_to_add = [str(i) for i in range(collection_size, limit)]
    print(f'\nComputing Dense Vectors for each passages .....')
    for passage_object in tqdm(passages_objects):
        passage_embedding = embedding_function(passage_object.passage_text)
        embeddings_to_add.append(passage_embedding)
        passages_to_add.append(passage_object.passage_text)
        metadata_to_add.append(passage_object.metadata)
    try:
        main_collection.upsert(ids=ids_to_add,
                            documents=passages_to_add,
                            embeddings=embeddings_to_add,
                            metadatas=metadata_to_add
                            )
    except Exception as e:
        print(f'Error: {e}')
        print(f'Only {len(passages_to_add)} passages_objects were added to the collection {collection_name}')

    print(f'{len(passages_to_add)} passages_objects were added to the collection {collection_name}')


def querying_to_db(chroma_client, collection_name, nl_query, embedding_model, n_results=3):
    """
    This function queries the database using a query and returns the results
    :param n_results: number of results to be returned
    :param chroma_client: ChromaClient object
    :param collection_name: name of the collection (SVD_for_documents_retrieval)
    :param nl_query: query to be used
    :param embedding_model: embedding function to be used
    :return: results
    """
    try:
        collection = chroma_client.get_collection(name=collection_name)
        query_embeddings = embedding_model(nl_query)
        results_set = collection.query(
            query_embeddings=[query_embeddings],
            n_results=n_results
        )
    except Exception as e:
        print(f'Error: {e}')
        results_set = None

    return results_set
