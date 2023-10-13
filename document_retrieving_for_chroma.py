from document_object import Document
from passage_object import PassageObject
from vector_database_manager import ChromaClient
from utils import build_document_object, get_page_number, get_chunks, get_documents_from_folder

path_to_pdf_folder = 'documents'
path_to_text_folder = 'extracted'

all_documents = get_documents_from_folder(path_to_pdf_folder)

# create a ChromaClient object
chroma_client = ChromaClient('chroma_db')

# TODO:  automatically create a collection and store the documents in it
