from models import SentenceBERTEmbedding
'''
    This file contains the global variables that are used in the project
'''
# 'SVD_for_documents_retrieval'
# 'SVD_for_documents_retrieval_mpnet_v2'
collection_name = 'SVD_for_documents_retrieval_mpnet_v2'
local_collection_path = 'chromadb'
host = '172.16.13.74'
port_number = '8000'
embedder = SentenceBERTEmbedding()