from models import SentenceBERTEmbedding

collection_name = 'SVD_for_documents_retrieval'
local_collection_path = 'chromadb'
host = '172.16.13.74'
port_number = '8000'
embedder = SentenceBERTEmbedding()