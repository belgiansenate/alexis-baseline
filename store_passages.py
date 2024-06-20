"""
    This file initializes a chromadb object and triggers the passages storing process
"""

from arguments import parse_args
from database_operations import passages_storing
from global_variables import local_collection_path, Mode

import chromadb

if __name__ == '__main__':
    args = parse_args()
    if args.mode == Mode.local:
        client = chromadb.PersistentClient(path=local_collection_path)
    else:
        client = chromadb.HttpClient(host=args.host, port=args.port)

    passages_storing(args.path, chromadb_client=client, collection_name=args.collection,
                     embedding_function=args.embedding, records_limit=args.limit
                     )

