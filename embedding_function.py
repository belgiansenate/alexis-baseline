import numpy
from chromadb import EmbeddingFunction, Embeddings
from transformers import BertTokenizer, BertModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib


# TODO: Finetune BERT or S-BERT model for senate documents

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

        return outputs.detach().tolist()


class TFIDFVectorizer(EmbeddingFunction):
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
