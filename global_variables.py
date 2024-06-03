from models import SentenceBERTEmbedding
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from FlagEmbedding import FlagReranker

'''
    This file contains the global variables that are used in the project
'''
# 'SVD_for_documents_retrieval'
# 'SVD_for_documents_retrieval_mpnet_v2'
collection_name = 'coll_bge_3m_full'
local_collection_path = 'chromadb_data_snt'
host = '172.16.13.74'
port_number = '8000'
embedder = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"}, query_instruction="Represent the query for passage retrieval: "
)
embeddings_all_MiniLM_L6_V2 = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
cross_encoder = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-large")
reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)