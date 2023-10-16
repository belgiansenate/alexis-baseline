import chromadb
from embedding_function import BERTEmbedding, TFIDFVectorizer
from vector_database_manager import ChromaClient, Mode
import pandas as pd

documents = ["Chess is called the game of kings. It has been around for a long time. People have been playing it for "
             "over 500 years. Chess is based on an even older game from India. The chess we play today is from Europe.",
             "Chess is a two-player game. One player uses the white pieces. The other uses the"
             "black pieces. Each piece moves in a special way. One piece is called the king. Each player has one. The "
             "players take turns moving their pieces. If a player lands on a piece, he or she takes it. The game ends "
             "when a player loses his or her king. There are a few more rules, but those are the basics.",
             "Some people think that chess is more than a game. They think that it makes the mind stronger. Good "
             "chess players use their brains. They take their time. They think about what will happen next. These "
             "skills are useful in life and in chess. Chess is kind of like a work out for the mind",
             "You don't always have lots of time to think when playing chess. There is a type of chess with short "
             "time limits. It's called blitz chess. In blitz chess, each player gets ten minutes to use for the whole "
             "game. Your clock runs during your turn. You hit the time clock after your move. This stops your clock. "
             "It also starts the other player's clock. If you run out of time, you lose. Games of blitz chess are "
             "fast-paced.",
             "Chess is not just for people. Computers have been playing chess since the 1970s. At first they did not "
             "play well. They made mistakes. As time went on they grew stronger. In 1997, a computer beat the best "
             "player in the world for the first time. It was a computer called Deep Blue. Deep Blue was big. It took "
             "up a whole room. By 2006 a cell phone could beat the best players in the world. Chess sure has come a "
             "long way. Don't you think so ?"]

emb_function = TFIDFVectorizer()
client = ChromaClient(path_directory='test_path_for_db', mode=Mode.local, embedding_function=emb_function)

collection = client.get_collection(name='test_chroma2')

collection.add(ids=[str(i+5) for i in range(len(documents))],
               documents=documents
        )
emb_function = TFIDFVectorizer('tfidf_vectorizer.pkl')
client = ChromaClient(path_directory='test_path_for_db', mode=Mode.local, embedding_function=emb_function)
collection = client.get_collection(name='test_chroma2')
results = collection.query(
    query_texts=["how do we usually call chess ?"],
    n_results=3
)
print(results)

