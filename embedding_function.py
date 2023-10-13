import numpy
from chromadb import EmbeddingFunction, Embeddings
from transformers import BertTokenizer, BertModel
import torch
from typing import List
from passage_object import PassageObject


# TODO: Finetune BERT or S-BERT model for senate documents

class MyEmbeddingFunction(EmbeddingFunction):

    def __init__(self, model_name='bert-base-multilingual-cased'):
        # initialize tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)

    def __call__(self, texts: PassageObject) -> Embeddings:
        # Tokenize the input texts
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        # Generate BERT embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        results = outputs.last_hidden_state.mean(dim=1).tolist()

        # Return the embeddings in Embeddings object
        # TODO : correct the output type because it does not match the expected type
        return results
