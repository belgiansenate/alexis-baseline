import numpy
from sentence_transformers import SentenceTransformer

from chromadb import EmbeddingFunction, Embeddings
from transformers import BertTokenizer, BertModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


# TODO: Finetune BERT or S-BERT model for senate documents
class SentenceBERTEmbedding(EmbeddingFunction):
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # initialize tokenizer and model
        self.model_name = model_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def __call__(self, texts) -> Embeddings:
        # Generate BERT embeddings
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        with torch.no_grad():
            outputs = self.model.encode(texts, convert_to_tensor=True)
        return outputs.detach().tolist()


class BERTEmbedding(EmbeddingFunction):

    def __init__(self, model_name='bert-base-multilingual-cased'):
        # initialize tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)

    def __call__(self, texts) -> Embeddings:
        # Tokenize the input texts
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        # Generate BERT embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
        outputs = outputs[0][:, 0, :]

        return outputs.detach().tolist()[0]


class TFIDFVectorizer(EmbeddingFunction):  # sklearn
    def __init__(self, existing_vectorizer=None):
        self.existing_vectorizer = existing_vectorizer
        if existing_vectorizer is not None:
            self.vectorizer = joblib.load(self.existing_vectorizer)
        else:
            self.vectorizer = TfidfVectorizer()

    def __call__(self, texts) -> Embeddings:
        if self.existing_vectorizer is not None:
            vectors = self.vectorizer.transform(texts)
        else:
            vectors = self.vectorizer.fit_transform(texts)
            # save_vectorizer
            joblib.dump(self.vectorizer, 'model_saved/tfidf_vectorizer.pkl')
        vectors = vectors.toarray().tolist()
        return vectors
