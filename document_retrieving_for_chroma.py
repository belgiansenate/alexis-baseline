from document_object import Document
from passage_object import PassageObject
from vector_database_manager import ChromaClient
from utils import build_document_object, get_page_number, get_chunks, get_documents_from_folder

# create a ChromaClient object
chroma_client = ChromaClient('chroma_db')


def processing_storing_to_db(path_to_pdf_folder, path_to_text_folder, db_name, collection_name):
    """
    This function processes the documents from a folder and stores them in a collection in the database.
    :param path_to_pdf_folder: path to the folder containing the pdf documents
    :param path_to_text_folder: path to the folder containing the extracted text documents
    :param db_name: name of the database
    :param collection_name: name of the collection
    :return: None
    """
    pdf_documents = get_documents_from_folder(path_to_pdf_folder)

    for pdf_document in pdf_documents:
        document = build_document_object(pdf_document, path_to_pdf_folder, path_to_text_folder)
