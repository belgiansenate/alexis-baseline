"""
    This file contains all the necessary methods to build the gradio interface, retrieve passages from chromadb and generate
    answers.
"""

import time
import os
import gradio as gr

from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from arguments import parse_args
from global_variables import local_collection_path, reranker, Mode
from utils import *

from langchain_community.vectorstores import Chroma
from langchain.retrievers import MergerRetriever

args = parse_args()
if args.mode == Mode.local:
    client = chromadb.PersistentClient(local_collection_path)
else:
    client = chromadb.HttpClient(args.host, args.port)

snt_vector_store_1 = Chroma(
    client=client,
    embedding_function=args.embedding[0],
    collection_name=args.collection[0]
)

snt_vector_store_2 = Chroma(
    client=client,
    embedding_function=args.embedding[1],
    collection_name=args.collection[1]
)

# code from = https://www.reddit.com/r/LangChain/comments/1acywew/is_there_a_reranking_example_with_langchain/
def rerank_docs(query, retrieved_docs, model):
    """
        Used to do the post-retrieval (reranking)
        :param query: the question
        :param retrieved_docs: the passages returned by the retriever
        :param model: the rerank model
        :return: a list of reranked pairs (passages - relevancy scores)
    """
    query_and_docs = [(query, r.metadata["passage_title"] + ": " + r.page_content) for r in retrieved_docs]
    scores = model.compute_score(query_and_docs)
    return sorted(list(zip(retrieved_docs, scores)), key=lambda x: x[1], reverse=True)


def answer_concat(texts, n_rerank):
    """
        Concatenate the results to be displayed
        :param texts: texts to be concatenated
        :param n_rerank: the final number of passages to be used as context
        :return: results
    """
    results = []
    hyperlink = "https://www.senate.be/www/webdriver?MItabObj=pdf&MIcolObj=pdf&MInamObj=pdfid&MItypeObj=application/pdf&MIvalObj="
    for i, text in enumerate(texts[:n_rerank]):
        results.append(
            f"<span style='color:red;'>Source {i + 1} ({text[0].metadata['leg_title']}, du {date_printing(text[0].metadata['date'])},"
            f"""titre : {text[0].metadata['passage_title']}, p.{text[0].metadata['page']})\nLien: {hyperlink + str(text[0].metadata['document_id'])}#page={str(text[0].metadata['page'])}.</span> \n {text[0].page_content}""")

    return '\n\n'.join(results)


def retrieve_from_vector_db(message, n_results_bge, n_results_allMini, n_rerank, language):
    """
        Retrieves relevant passages from a collection in chromadb
        :param message: the query
        :param n_results_bge: number of results to be returned by the first retriever (BGE m3)
        :param n_results_allMini: number of results to be returned by the second retriever (all-MiniLM-L6-v2)
        :param n_rerank: the final number of passages to be used as context
        :param language: either French or Dutch
        :return: the context to be used by the generator to answer the given queries
    """
    try:
        retriever_all_mini = snt_vector_store_2.as_retriever(search_type="mmr", search_kwargs={
            'filter': {'language': str(language)},
            "k": n_results_allMini,
            'fetch_k': 250,
            'lambda_mult': 0.1
        })
        retriever_BGE_full_old = snt_vector_store_1.as_retriever(search_type="mmr", search_kwargs={
            'filter': {'language': str(language)},
            "k": n_results_bge,
            'fetch_k': 250,
            'lambda_mult': 0.9,
        })

        lotr = MergerRetriever(retrievers=[retriever_BGE_full_old, retriever_all_mini])
        rel_text_BGE = lotr.get_relevant_documents(message)

        relevant_docs = rerank_docs(message, rel_text_BGE, reranker)

    except Exception as e:
        print(e)
        return "Sorry, I couldn't find any answer to your question", message

    
    return relevant_docs, answer_concat(relevant_docs, n_rerank)


def echo_chunks(message, chat_history, languages, n_result_bge, n_results_allmini, n_rerank):
    """
        Used to handle the messages in the retrieval interface (chatbot and the user's messages)
        :param message: the query
        :param chat_history: the history of the conversation (questions + chatbot responses)
        :param languages: either French or Dutch
        :param n_result_bge: number of results to be returned by the first retriever (BGE m3)
        :param n_results_allmini: number of results to be returned by the second retriever (all-MiniLM-L6-v2)
        :param n_rerank: the final number of passages to be used as context
        :return: The given response by the chatbot + the history of the conversation
    """
    _, bot_message = retrieve_from_vector_db(message, n_result_bge, n_results_allmini, n_rerank, languages)
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


def user(message, chat_history):
    """
        Handles the input text (the user's question (query))
        :param message: the query
        :param chat_history: the history of the conversation (pairs of question + chatbot response)
        :return: displays the user's question (in the gradio interface) + keeps track of the conversation's history
    """
    chat_history = chat_history + [[message, None]]
    print(f"chat history = \n{chat_history}")
    return gr.Textbox(value="", interactive=False), chat_history


def respond(chat_history, n_results_bge, n_results_allMini, n_rerank, model, language,
            ):
    """
        Used in the generation interface, it returns the final answer generated by the used LLM inside the generator
        :param chat_history: the history of the conversation (pairs of question + chatbot response)
        :param n_results_bge: number of results to be returned by the first retriever (BGE m3)
        :param n_results_allMini: number of results to be returned by the second retriever (all-MiniLM-L6-v2)
        :param n_rerank: the final number of passages to be used as context
        :param model: the LLM to be used inside the generator
        :param language: either French or Dutch
        :return: the final answer generated by the chatbot
    """
    _, context = retrieve_from_vector_db(chat_history[-1][0], n_results_bge, n_results_allMini, n_rerank, language)
    chat_history[-1][1] = ""

    ### LLM
    prompt = ""
    local_llm = ""
    if model == "Llama_3_8B":
        local_llm = "llama3"

        if language == "fr":
            prompt = PromptTemplate(
                template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|> Vous êtes un assistant chargé de répondre à des questions.
                Utilisez les informations de contexte suivantes pour fournir une réponse. Si vous ne connaissez pas la réponse, dites simplement que vous ne savez pas.
                Faites en sorte que la réponse soit concise mais détaillée.
                Donnez un lien vers le document original.<|eot_id|><|start_header_id|>user<|end_header_id|>
                Question: {question} 
                Context: {context} 
                Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
                input_variables=["question", "context"],
            )
        elif language == "nl":
            prompt = PromptTemplate(
                template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>Je bent een assistent die vragen beantwoordt.
                Gebruik de volgende context informatie om de vraag te beantwoorden. Als je het antwoord niet weet, zeg dan gewoon dat je het niet weet.
                Schrijf in het Nederlands.
                Houd het antwoord beknopt maar geef details.
                Geef een link naar het originele document.<|eot_id|><|start_header_id|>user<|end_header_id|>
                Question: {question} 
                Context: {context} 
                Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
                input_variables=["question", "context"],
            )
    if model == "Aya_23_35B":
        local_llm = "aya:35b-23-q4_K_M"

        if language == "fr":
            prompt = PromptTemplate(
                template="""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>Vous êtes un assistant chargé de répondre à des questions.
                Utilisez les informations de contexte suivantes pour fournir une réponse. Si vous ne connaissez pas la réponse, dites simplement que vous ne savez pas.
                Faites en sorte que la réponse soit concise mais détaillée.
                Donnez un lien vers le document original.<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>
                Question: {question} 
                Context: {context} 
                <|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>    <|END_OF_TURN_TOKEN|>""",
                input_variables=["question", "context"],
            )
        elif language == "nl":
            prompt = PromptTemplate(
                template="""<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>Je bent een assistent die vragen beantwoordt.
                Gebruik de volgende context informatie om de vraag te beantwoorden. Als je het antwoord niet weet, zeg dan gewoon dat je het niet weet.
                Schrijf in het Nederlands.
                Houd het antwoord beknopt maar geef details.
                Geef een link naar het originele document.<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|USER_TOKEN|>
                Question: {question} 
                Context: {context} 
                <|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>    <|END_OF_TURN_TOKEN|>""",
                input_variables=["question", "context"],
            )

    llm = ChatOllama(model=local_llm, temperature=0.7, max_output_tokens=1000)

    rag_chain = prompt | llm | StrOutputParser()

    # Run
    question = chat_history[-1][0]

    bot_message = rag_chain.invoke({"context": context, "question": question})

    for character in bot_message:
        chat_history[-1][1] += character
        time.sleep(0.01)
        yield chat_history


title_markdown = ("""
<div style="text-align: center; font-size: 32px;">
    Alexis Senate Chatbot \U0001F916
</div>
<h5 style="font-size: 16px;"> \u26A0\uFE0F Guide \u26A0\uFE0F: The main goal of the guide is to explain how to use the retriever and the generator to ask and get answers from the conversationnal agent</h5>
<ol style="margin-left: 20px; font-size: 16px">
    <li>Please chose the language you want (nl or fr)</li>
    <li>First, the retriever is used to get the passages from the database used by the chatbot.</li>
    <li>You have to choose the number of passages to look for in both retrievers (allMini & BGE).</li>
    <li>Please select the number of final results you want (Number of final passages).</li>
    <li> The higher the number of final passages, the longer the computation time</li>
    <li> Please select the model you want to use for the generation, either Llama 3 8B or Aya 23 35B. The second model takes too much time but performs in both french and dutch.</li>
    <li> Llama 3 in not capable to answer in dutch </li>
</ol>

<p style="border: 2px solid black; padding: 10px; display: inline-block;"> <strong> **Note**: This version is not perfect. It may return some passages which are not related to the question \U0001F605. It uses open source models with lower precision to run them locally.</strong></p>

""")

with gr.Blocks() as demo:
    gr.Markdown(title_markdown)
    with gr.Tab("retrieval"):
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Accordion("Parameters"):
                    n_results_BGE = gr.Slider(minimum=1, value=50, step=1,
                                              label="Number of BGE passages",
                                              info="Number of passages to be returned by the 1st retriever")
                    n_results_AllMINI = gr.Slider(minimum=1, value=50, step=1,
                                                  label="Number of AllMINI passages",
                                                  info="Number of passages to be returned by the 2nd retriever")
                    n_rerank = gr.Slider(minimum=1, value=1, maximum=50 , step=1,
                                         label="Number of final results")
                    language = gr.Radio(
                        ["fr", "nl"],
                        label="Languages")
            with gr.Column(scale=6):
                chatbot = gr.Chatbot(
                    [],
                    label="Alexis \U0001F916",
                    show_label=True,
                    height=500,
                    bubble_full_width=False,
                    show_copy_button=True,
                    avatar_images=("Images/Human.jpg", "Images/senate.jpg")
                )
                with gr.Row():
                    with gr.Column(scale=8):
                        msg = gr.Textbox(
                            label="Enter your question here",
                            show_label=True
                        )
                        clear = gr.ClearButton([msg, chatbot, n_results_BGE, n_results_AllMINI, n_rerank, language], value="Clear All")

        msg.submit(echo_chunks, [msg, chatbot,  language, n_results_BGE, n_results_AllMINI, n_rerank], [msg, chatbot])

    with gr.Tab("generation"):
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Accordion("Models"):
                    selected_model = gr.Radio(
                        ["Llama_3_8B", "Aya_23_35B"],
                        label="Available models")
                with gr.Accordion("Parameters"):
                    n_results_BGE = gr.Slider(minimum=1, value=50, step=1,
                                              label="Number of BGE passages",
                                              info="Number of passages to be returned by the 1st retriever")
                    n_results_AllMINI = gr.Slider(minimum=1, value=50, step=1,
                                                  label="Number of AllMINI passages",
                                                  info="Number of passages to be returned by the 2nd retriever")
                    n_rerank_gen = gr.Slider(minimum=1, value=1, maximum=10, step=1,
                                                  label="Number of final passages")
                    language_generation = gr.Radio(
                        ["fr", "nl"],
                        label="Languages",
                        info= "Select the language to get answers in that particular language"
                    )
            with gr.Column(scale=6):
                chatbot = gr.Chatbot(
                    [],
                    label="Alexis \U0001F916",
                    show_label=True,
                    height=500,
                    bubble_full_width=False,
                    show_copy_button=True,
                    avatar_images=("Images/Human.jpg", "Images/senate.jpg")
                )
                with gr.Row():
                    with gr.Column(scale=8):
                        text = gr.Textbox(
                            label="Enter your question here",
                            show_label=True
                        )
                    clear = gr.ClearButton([text, chatbot, n_results_BGE, n_results_AllMINI, n_rerank_gen, language_generation], value="Clear All")


        text_message = text.submit(user, [text, chatbot], [text, chatbot], queue=False).then(
            respond, [chatbot, n_results_BGE, n_results_AllMINI, n_rerank_gen, selected_model, language_generation],
            chatbot
        )
        text_message.then(lambda: gr.Textbox(interactive=True), None, [text], queue=False)

if __name__ == "__main__":
    demo.queue()
    usr = os.getenv('GRADIO_USERNAME')
    pwd = os.getenv('GRADIO_PASSWORD')
    demo.launch(auth=(usr, pwd), server_name="*")
