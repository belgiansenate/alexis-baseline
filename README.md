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
  
| Model | Embedding size | Context window | Multilingual |
| ----- | -------------- | -------------- | ------------ |
| BAAI/bge-m3|1024 | 8192 | Yes |
| all-MiniLM-L6-v2 | 384 | 256 | Some capabilities |

  <p>Embedding models</p>
</div>
