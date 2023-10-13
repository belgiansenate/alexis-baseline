import chromadb
from embedding_function import MyEmbeddingFunction
from vector_database_manager import ChromaClient, Mode

emb_function = MyEmbeddingFunction()
client = ChromaClient(path_directory='chroma_db', mode=Mode.local)
collection = client.get_collection(name='chroma', embedding_function=emb_function)
collection.update(ids=['4', '5', '6'],
                  documents=["Metal detectors make magnetic waves. These waves go through the ground. The waves change "
                             "when they hit metal. Then the device beeps. This lets the person with the device know "
                             "that"
                             "metal is close.",
                             "The first metal detectors were meant to help miners. They were big. They cost a lot of "
                             "money. They used a lot of power. And worst of all, they didn't work well. People kept "
                             "trying to make them better.",
                             "These devices also make clothes safer. It sounds funny, but it's true. Most clothes are "
                             "made in big factories. There are lots of needles in these places. Needles break from time"
                             "to time. They get stuck in the clothes. They would poke people trying them on. They don't"
                             "though. That's because our clothes are scanned for metal. Isn't that nice? Let's hear it "
                             "for metal detectors. They make the world a safer place."],
                  metadatas=[{"source": "my_source3"}, {"source": "my_source4"}, {"source": "my_source5"}]
                  )

# client = ChromaClient(path_directory='chroma_db', mode=Mode.local)
# collection = client.get_collection(name='chroma.sqlite3', embedding_function=emb_function)
# print(len(collection.peek()['embeddings'][0]))
