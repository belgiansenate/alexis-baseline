[![Alexis Baseline 🤖](https://img.shields.io/badge/Introduction-blue)](#alexis-baseline-)
[![Approach](https://img.shields.io/badge/Approach-green)](#approach)
[![Embedding - rerank models](https://img.shields.io/badge/Embedding-rerank-blue)](#embedding---rerank-models)
[![Large Language Models (LLMs)](https://img.shields.io/badge/LLMs-red)](#large-language-models-llms)
[![Some useful links](https://img.shields.io/badge/links-yellow)](#some-useful-links)

# Alexis Baseline 🤖

The Belgian Senate is an important institution that generates a large quantity of official documents every year, such as laws, ordinances, declarations and reports. These documents contain valuable and often complex information that can be difficult for citizens to understand. This is where a specialized ChatBot can play an important role. Using the latest natural language processing technologies, the Alexis chatbot aims to understand the questions asked by users and provide precise, clear answers based on the documents generated by the Belgian Senate.


# Approach

Our chatbot utilizes a *Retrieval Augmented Generation (RAG)* architecture, designed to enhance question answering systems by integrating a datastore, retriever, and generator components. The architecture aims to provide accurate and contextually relevant answers to user queries. Here’s an overview of each component and its role in the system:
1. **Datastore**: Which is central to our approach. It stores relevant passages as embeddings. These passages serve as the knowledge base from which the system retrieves information to answer user questions. We use [chromadb](https://www.trychroma.com/) for this purpose.
2. **Retriever**: The retriever component is responsible for retrieving the most relevant passages from the datastore based on the user's input question. This initial retrieval phase is crucial as it sets the context for generating accurate answers. We adopt the *[Lord Of The Retrievers (LOTR)](https://python.langchain.com/v0.1/docs/integrations/retrievers/merger_retriever/)* which is designed in order to merge several retrievers and exploit their different strengths.
   - **First retriever**: This retriever excels in both French and Dutch languages and demonstrates strong semantic understanding of words and sentences within passages. It efficiently retrieves relevant information across a wide range of contexts.
   - **Second Retriever**: Handles small texts such as votes, this retriever complements the first one by focusing on precision and accuracy in retrieving concise information.  
4. **Generator**: Once relevant passages are retrieved, the generator component processes the user question along with these passages to generate a coherent and informative answer. This generation process ensures that the response is not only relevant but also comprehensively addresses the query. This process is done using *Large Language Models (LLMs)*.
5. **Post-Retrieval Phase**: To improve the quality of retrieved passages, a post-retrieval phase employs a rerank method. This method involves using a rerank model to evaluate and score question-passage pairs independently. The reranking process aims to prioritize passages with higher relevancy scores, thereby enhancing the effectiveness of subsequent answer generation.<br>
<br>
The next Figure shows the design of this architecture:
<div align="center">
  <img src="https://github.com/belgiansenate/alexis-baseline/assets/56476929/fa8958df-7f22-4084-812e-f27aa9e0fcfb" alt="ARAG" width="175"/>
</div>
<p>(<i> source </i>: Yunfan Gao, Yun Xiong, Xinyu Gao, Kangxiang Jia, Jinliu Pan, Yuxi Bi, Yi Dai, Jiawei Sun, Meng Wang, Haofen Wang. Retrieval-Augmented Generation for Large Language Models : A Survey. URL: https://arxiv.org/abs/2312.10997)</p>

# Embedding - Rerank models

This sections shows the models used to encode the passages (embedding models) and to do the post-retrieval process (rerank model). 
<div align="center">
  
| Embedding model | Embedding size | Context window | Multilingual? |
| ----- | -------------- | -------------- | ------------ |
| [BAAI/bge-m3](https://github.com/FlagOpen/FlagEmbedding)|1024 | 8192 tokens | Yes |
| [all-MiniLM-L6-v2](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html) | 384 | 256 tokens | Some capabilities |

  <p>Embedding models used in the project</p>
</div>
<br>
<div align="center">
  
| Rerank model | Base model | Multilingual? |
| -------------------- | ---------- | ------------- |
| [BAAI/bge-reranker-v2-m3](https://github.com/FlagOpen/FlagEmbedding)| BAAI/bge-m3 | Yes |

  <p>Rerank model used in the project</p>
</div>

# Large Language Models (LLMs)

In this project, the bilingual (French & Dutch) capability was a significant factor. Among the models evaluated, only a few demonstrated strong performance in Dutch. Several models showed strong performance in both French and English. Ultimately, two models were chosen: the first excels in generating high-quality responses in French but falls short in Dutch due to limited training data and lower precision. The second model is a novel multi-language model, capable of performing in 23 languages including French and Dutch. It is based on a new research approach advocating for the development of language models focused on a smaller number of languages, but with extensive and diverse datasets for each language, rather than attempting to cover a vast number of languages with less comprehensive data. 

<div align="center">
  
| Large Language Model | Number of parameters | Multilingual? | Precision |
| -------------------- | -------------------- |-------------- | --------- |
| [Meta Llama 3](https://llama.meta.com/llama3/)  | 8B | Some capabilities | q4_K_M |
| [Cohere Aya 23](https://cohere.com/research/papers/aya-command-23-8b-and-35b-technical-report-2024-05-23) | 35B | Yes | q4_K_M |         
  <p>LLMs used in the project</p>
</div>

# Some useful links
- https://www.langchain.com/
- https://llama.meta.com/llama3/
- https://cohere.com/research/papers/aya-command-23-8b-and-35b-technical-report-2024-05-23
- https://github.com/FlagOpen/FlagEmbedding
- https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
- https://python.langchain.com/v0.1/docs/integrations/retrievers/merger_retriever/
- https://www.trychroma.com/
- https://arxiv.org/abs/2312.10997
