from transformers import BertTokenizer, BertModel
import torch
from typing import List


class MyEmbeddingFunction:
    def __init__(self, model_name='bert-base-multilingual-cased'):
        # initialize tokenizer and model
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)

    def __call__(self, texts: List[str]) -> List[torch.Tensor]:
        # Tokenize the input texts
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        # Generate BERT embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Return embeddings as a numpy array
        return outputs.last_hidden_state.mean(dim=1).detach().numpy()
