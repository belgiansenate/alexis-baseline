from document_processing import  build_passages_objects
from utils import get_documents_from_folder
from embedding_function import TFIDFVectorizer
from vector_database_manager import ChromaClient, Mode


def processing_storing_to_db(path_to_pdf_folder, path_to_text_folder, chromadb_client: ChromaClient, collection_name):
    """
    This function processes the passages_objects from a folder and stores them in a collection in the database.
    :param chromadb_client: ChromaClient object
    :param path_to_pdf_folder: path to the folder containing the pdf passages_objects
    :param path_to_text_folder: path to the folder containing the extracted text passages_objects
    :param collection_name: name of the collection (SVD_for_documents_retrieval)
    :return: None
    """
    pdf_documents = get_documents_from_folder(path_to_pdf_folder)
    passages_objects = []

    for pdf_document in pdf_documents:
        french_passages_objects, dutch_passages_objects, _, _ = build_passages_objects(
            pdf_document, path_to_pdf_folder,path_to_text_folder
        )
        passages_objects.extend(french_passages_objects)
        passages_objects.extend(dutch_passages_objects)

    collection = chromadb_client.get_collection(collection_name)
    collection_size = collection.count()

    documents_to_add = []
    metadata_to_add = []
    ids_to_add = []

    for passage_object in passages_objects:

        ################################ Provisional Solution ###########################
        chunks_size = 2
        limit = collection_size + chunks_size
        for i in range(collection_size, limit):
            ids_to_add.append(str(i))
        documents_to_add.append(passage_object.french_text)
        documents_to_add.append(passage_object.dutch_text)
        metadata_to_add.append(passage_object.metadata)
        metadata_to_add.append(passage_object.metadata)
        collection_size = limit
        ################################ Provisional Solution ###########################

    collection.add(ids=ids_to_add,
                   documents=documents_to_add,
                   metadatas=metadata_to_add
                   )
    print(f'{len(documents_to_add)} passages_objects were added to the collection {collection_name}')


################################ storing documents ###########################
embedding_function = TFIDFVectorizer()
client = ChromaClient(path_directory='test_path_for_db', mode=Mode.local, embedding_function=embedding_function)
collection_name = 'test_collection'
collection = client.get_collection(name=collection_name)
processing_storing_to_db(path_to_pdf_folder='documents', path_to_text_folder='extracted',
                         collection_name=collection_name, chromadb_client=client)
################################ storing documents ###########################


################################  querying using TF-IDF ###########################
embedding_function = TFIDFVectorizer('model_saved/tfidf_vectorizer.pkl')
client = ChromaClient(path_directory='test_path_for_db', mode=Mode.local, embedding_function=embedding_function)
query = "ask a question about the document"
results = collection.query(
    query_texts=[query],
    n_results=3
)
print(results)
################################  querying using TF-IDF ###########################
