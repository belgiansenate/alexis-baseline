from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings
from FlagEmbedding import FlagReranker
from enum import Enum
#from models import *

'''
    This file contains the global variables that are used in the project
'''


class Mode(Enum):
    host = 'host'
    local = 'local'


collection_name_bge = 'coll_bge_3m_full'
collection_name_all_mini = 'new_all_miniLM_L6_coll'
local_collection_path = 'chromadb_data_snt'

host = '172.16.13.74'
port_number = '8000'

embedder = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    query_instruction="Represent the query for passage retrieval: "
    )
"""CustomHuggingFaceBgeEmbeddings()"""

embeddings_all_MiniLM_L6_V2 = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
    )
"""CustomHuggingFaceEmbeddings()"""

reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)
