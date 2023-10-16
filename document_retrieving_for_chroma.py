from document_object import Document
from passage_object import PassageObject
from embedding_function import TFIDFVectorizer
from vector_database_manager import ChromaClient, Mode
from utils import build_document_object, get_page_number, get_chunks, get_documents_from_folder


def processing_storing_to_db(path_to_pdf_folder, path_to_text_folder, chromadb_client: ChromaClient, collection_name):
    """
    This function processes the documents from a folder and stores them in a collection in the database.
    :param chromadb_client: ChromaClient object
    :param path_to_pdf_folder: path to the folder containing the pdf documents
    :param path_to_text_folder: path to the folder containing the extracted text documents
    :param collection_name: name of the collection (SVD_for_documents_retrieval)
    :return: None
    """
    pdf_documents = get_documents_from_folder(path_to_pdf_folder)
    documents = []

    for pdf_document in pdf_documents:
        document = build_document_object(pdf_document, path_to_pdf_folder, path_to_text_folder)
        documents.append(document)

    collection = chromadb_client.get_collection(collection_name)
    collection_size = collection.count()
    documents_to_add = []
    metadata_to_add = []
    ids_to_add = []

    for document in documents:
        # TODO : implement passage extraction
        ################################ Provisional Solution ###########################
        chunks_size = 2
        limit = collection_size + chunks_size
        for i in range(collection_size, limit):
            ids_to_add.append(str(i))
        documents_to_add.append(document.french_text)
        documents_to_add.append(document.dutch_text)
        metadata_to_add.append(document.metadata)
        metadata_to_add.append(document.metadata)
        collection_size = limit
        ################################ Provisional Solution ###########################

    collection.add(ids=ids_to_add,
                   documents=documents_to_add,
                   metadatas=metadata_to_add
                   )
    print(f'{len(documents_to_add)} documents were added to the collection {collection_name}')


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
