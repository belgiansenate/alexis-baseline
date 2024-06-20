[![Alexis Baseline 🤖](https://img.shields.io/badge/Welcome-blue)](#Alexis-Baseline🤖)
[![Approach](https://img.shields.io/badge/Welcome-blue)](#Approach)
[![Embedding - rerank models](https://img.shields.io/badge/Welcome-blue)](#Embedding---rerank-models)
[![Large Language Models (LLMs)](https://img.shields.io/badge/Welcome-blue)](#large-language-models-llms)


# Alexis Baseline 🤖

The Belgian Senate is an important institution that generates a large quantity of official documents every year, such as laws, ordinances, declarations and reports. These documents contain valuable and often complex information that can be difficult for citizens to understand. This is where a specialized ChatBot can play an important role. Using the latest natural language processing technologies, the Alexis chatbot aims to understand the questions asked by users and provide precise, clear answers based on the documents generated by the Belgian Senate.


# Approach

We decided to use an approach based on a Retrieval Augmented Generation (RAG) architecture which consists on having a datastore to store our relavant passages as embeddings, a retriever which consists on returning most likely relevant passages from the datastore to a question asked by the user (as an input) and finally a generator which takes a question and the relevant passages as input and generates an answer based on the given passages in the output. 
A post-retrieval phase is necessary to get better passages in the first ranks. In this project, we decided to use the rerank method using a rerank model in order to create pairs (question - passage). These pairs are analysed separately in order to computer a relevancy score for each of them. Once the new scores are computed, the passages are reranked (best ones at first). 
The next figure shows how this can be designed.
<div align="center">
  <img src="https://github.com/belgiansenate/alexis-baseline/assets/56476929/fa8958df-7f22-4084-812e-f27aa9e0fcfb" alt="ARAG" width="175"/>
</div>
<p>(source: Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, Meng Wang, Haofen Wang. Retrieval-Augmented Generation for Large Language Models : A Survey. URL: https://arxiv.org/abs/2312.10997)</p>
Since the passages we have are sometimes small (like votes), we decided to merge two retrievers. The first one performs well in both French and Dutch and better understands the meaning of the words and sentences in the passages. The second model performs well in small texts like votes (which was not possible using the first retriever). This approach is called Lord Of The Retrievers (LOTR) (https://python.langchain.com/v0.1/docs/integrations/retrievers/merger_retriever/). After that, a rerank process is done using a multilingual rerank model. Finaly, the generation is done using a Large Language Model (LLM).

# Embedding - rerank models

This sections shows the models used to encode the passages (embedding models) and to do the post-retrieval process (rerank model). 
<div align="center">
  
| Embedding model | Embedding size | Context window | Multilingual? |
| ----- | -------------- | -------------- | ------------ |
| [BAAI/bge-m3](https://github.com/FlagOpen/FlagEmbedding)|1024 | 8192 | Yes |
| [all-MiniLM-L6-v2](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html) | 384 | 256 | Some capabilities |

  <p>Embedding models used in the project</p>
</div>

<div align="center">
  
| Rerank model | Base model | Multilingual? |
| -------------------- | ---------- | ------------- |
| [BAAI/bge-reranker-v2-m3](https://github.com/FlagOpen/FlagEmbedding)| BAAI/bge-m3 | Yes |

  <p>Rerank model used in the project</p>
</div>

# Large Language Models (LLMs)

In this project, the bilingual (French & Dutch) aspect was important. Only a small number of models were trained and perform well in Dutch. Several models perform well in both French and English. Two models were selected, the first one generate a really good answers in French but not in dutch as it is used in low precision and is not trained on a large content in Dutch.
The second model is a new model performing in 23 languages (French & Dutch included). It is built on a new research which states that instead of building and training LLMs on several languages (like 100), build models on a small number of languages but witch large content and datasets in every language. 

<div align="center">
  
| Large Language Model | Number of parameters | Multilingual? | Precision |
| -------------------- | -------------------- |-------------- | --------- |
| [Meta Llama 3](https://llama.meta.com/llama3/)  | 8B | Some capabilities | q4_K_M |
| [Cohere Aya 23](https://cohere.com/research/papers/aya-command-23-8b-and-35b-technical-report-2024-05-23) | 35B | Yes | q4_K_M |         
  <p>LLMs used in the project</p>
</div>
