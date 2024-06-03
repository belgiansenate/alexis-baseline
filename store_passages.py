from arguments import parse_args
from database_operations import passages_storing
from vector_database_manager import Mode, ChromaClient

if __name__ == '__main__':
    args = parse_args()
    if args.mode == Mode.local:
        client = ChromaClient(mode=Mode.local, path_directory='chromadb')
    else:
        client = ChromaClient(host=args.host, mode=Mode.host, port_number=args.port)

    client.get_or_create_collection(args.collection)
    passages_storing(args.path, chromadb_client=client, collection_name=args.collection,
                     embedding_function=args.embedding,records_limit=args.limit
                     )
