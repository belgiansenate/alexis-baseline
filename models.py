import torch
from sentence_transformers import SentenceTransformer
from transformers import BertTokenizer, BertModel
from chromadb import EmbeddingFunction, Embeddings


# TODO: Finetune BERT or S-BERT model for senate documents

#all-MiniLM-L6-v2 (fast but less efficient, the default one)
#all-mpnet-base-v2
class SentenceBERTEmbedding(EmbeddingFunction):
    def __init__(self, model_name='all-mpnet-base-v2'):
        # initialize tokenizer and model
        self.model = SentenceTransformer(model_name, device='cuda' if torch.cuda.is_available() else 'cpu')

    def __call__(self, texts) -> Embeddings:
        # Generate BERT embeddings
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
