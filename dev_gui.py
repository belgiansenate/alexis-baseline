import csv
import re
import time
import os
import gradio as gr
from datetime import datetime

from langchain import hub
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, RetrievalQA
from langchain_community.llms import LlamaCpp
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from gradio import Slider

from arguments import parse_args
from database_operations import querying_to_db
from vector_database_manager import ChromaClient, Mode
from global_variables import local_collection_path, cross_encoder, embeddings_all_MiniLM_L6_V2, reranker

from llama_cpp import Llama
from langchain_community.vectorstores import Chroma
from langchain.retrievers.document_compressors.cross_encoder_rerank import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever, MergerRetriever

args = parse_args()
if args.mode == Mode.local:
    snt_vector_db1 = Chroma(
        persist_directory=local_collection_path,
        embedding_function=args.embedding,
        collection_name="coll_bge_3m_full"
    )

    snt_vector_new = Chroma(
        persist_directory=local_collection_path,
        embedding_function=embeddings_all_MiniLM_L6_V2,
        collection_name="new_all_miniLM_L6_coll"
    )

else:
    client = ChromaClient(host=args.host, mode=Mode.host, port_number=args.port)
    client.get_or_create_collection(args.collection)


# code from = https://www.reddit.com/r/LangChain/comments/1acywew/is_there_a_reranking_example_with_langchain/
def rerank_docs(query, retrieved_docs, model):
    query_and_docs = [(query, r.metadata["passage_title"] + ": " + r.page_content) for r in retrieved_docs]
    scores = model.compute_score(query_and_docs)
    return sorted(list(zip(retrieved_docs, scores)), key=lambda x: x[1], reverse=True)


def date_printing(date):
    date_format = '%Y-%m-%d %H:%M:%S'
    return ((datetime.strptime(date, date_format)).date()).strftime("%d/%m/%Y")


def answer_concat(texts, n_rerank):
    """
    Concatenate the results to be displayed
    :param texts: texts to be concatenated
    :param metadata: metadata to be concatenated
    :return:   results
    """
    results = []
    hyperlink = "https://www.senate.be/www/webdriver?MItabObj=pdf&MIcolObj=pdf&MInamObj=pdfid&MItypeObj=application/pdf&MIvalObj="
    for i, text in enumerate(texts[:n_rerank]):
        results.append(
            f"<span style='color:red;'>Source {i + 1} ({text[0].metadata['leg_title']}, du {date_printing(text[0].metadata['date'])},"
            f"""titre : {text[0].metadata['passage_title']}, p.{text[0].metadata['page']})\nLien: {hyperlink + str(text[0].metadata['document_id'])}#page={str(text[0].metadata['page'])}.</span> \n {text[0].page_content}""")

    return '\n\n'.join(results)


def retrieve_from_vector_db(message, n_results_bge, n_results_allMini, n_rerank, language):
    try:
        """
        results = querying_to_db(chroma_client=client, collection_name=args.collection, nl_query=message,
                                 embedding_model=args.embedding, n_results=n_results)
        """

        retriever_all_mini = snt_vector_new.as_retriever(search_type="similarity", search_kwargs={
            'filter': {'language': str(language)},
            "k": n_results_allMini,
            'fetch_k': 250,
            'lambda_mult': 0.1
        })
        retriever_BGE_full_old = snt_vector_db1.as_retriever(search_type="mmr", search_kwargs={
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

    # error : File name too long
    #return rel_text_BGE, answer_concat(rel_text_BGE, n_rerank)
    return rel_text_BGE, answer_concat(rel_text_BGE, n_rerank)


def echo_chunks(message, chat_history, languages, n_result_bge, n_results_allmini, n_rerank):
    _, bot_message = retrieve_from_vector_db(message, n_result_bge, n_results_allmini, n_rerank, languages)
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


def user(message, chat_history):
    chat_history = chat_history + [[message, None]]
    print(f"chat history = \n{chat_history}")
    return gr.Textbox(value="", interactive=False), chat_history


def format_docs(docs):
    results = []
    hyperlink = "https://www.senate.be/www/webdriver?MItabObj=pdf&MIcolObj=pdf&MInamObj=pdfid&MItypeObj=application/pdf&MIvalObj="
    for i, doc in enumerate(docs):
        results.append(
            f"<span style='color:red;'>Source {i + 1} ({doc.metadata['leg_title']}, du {date_printing(doc.metadata['date'])},"
            f"""titre : {doc.metadata['passage_title']}, p.{doc.metadata['page']})\nLien: {hyperlink + str(doc.metadata['document_id'])}#page={str(doc.metadata['page'])}.</span> \n {doc.page_content}""")

    return '\n\n'.join(results)


# Todo: try to add prompts template for each of the models into the interface.
def respond(chat_history, n_results_bge, n_results_allMini, n_rerank, model, language,
            ):
    _, context = retrieve_from_vector_db(chat_history[-1][0], n_results_bge, n_results_allMini, n_rerank, language)
    chat_history[-1][1] = ""

    retriever_all_mini = snt_vector_new.as_retriever(search_type="mmr", search_kwargs={
        'filter': {'language': str(language)},
        "k": int(n_results_allMini),
        'fetch_k': 250,
        'lambda_mult': 0.1
    })
    retriever_BGE_full_old = snt_vector_db1.as_retriever(search_type="mmr", search_kwargs={
        'filter': {'language': str(language)},
        "k": int(n_results_bge),
        'fetch_k': 250,
        'lambda_mult': 0.9,
    })

    lotr = MergerRetriever(retrievers=[retriever_BGE_full_old, retriever_all_mini])

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

    llm = ChatOllama(model=local_llm, temperature=0.7, max_output_tokens=500)

    rag_chain = prompt | llm | StrOutputParser()

    # Run
    question = chat_history[-1][0]
    docs = lotr.get_relevant_documents(question)

    after_rerank = rerank_docs(question, docs, reranker)

    bot_message = rag_chain.invoke({"context": answer_concat(after_rerank, n_rerank), "question": question})

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
    <li>First, the retriever is used to get the passages from the database used by the chatbot.</li>
    <li>You have to choose the number of passages to look for in both retrievers (allMini & BGE)</li>
    <li>Since it is a first version which is not complete, you have to chose the number of passages you want.</li>
    <li>Please chose the language you want (nl or fr)</li>
    <li> Please select the model you want to use for the generation, either Llama 3 8B or Aya 23 35B. The second model takes too much time but performs in both french and dutch</li>
    <li> Llama 3 in not capable to answer in dutch </li>
</ol>

<p style="border: 2px solid black; padding: 10px; display: inline-block;"> <strong> **Note**: This version is not perfect since it will return some passages which are not related to the question \U0001F605. The goal when building the dataset is to specialize the chatbot on the Senate documents by: training, testing and validation. Even if we do not use it for training, it stills important to have it.</strong></p>

""")
with gr.Blocks() as demo:
    gr.Markdown(title_markdown)
    with gr.Tab("retrieval"):
        with gr.Row():
            with gr.Column(scale=3):
                with gr.Accordion("Parameters"):
                    n_results_BGE = gr.Slider(minimum=1, value=50, maximum=100, step=1,
                                              label="Number of BGE passages",
                                              info="Number of passages to be returned by the 1st retriever")
                    n_results_AllMINI = gr.Slider(minimum=1, value=50, maximum=100, step=1,
                                                  label="Number of AllMINI passages",
                                                  info="Number of passages to be returned by the 2nd retriever")
                    n_rerank = gr.Slider(minimum=1, value=1, maximum=50, step=1,
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
                    n_results_BGE = gr.Slider(minimum=1, value=50, maximum=100, step=1,
                                              label="Number of BGE passages",
                                              info="Number of passages to be returned by the 1st retriever")
                    n_results_AllMINI = gr.Slider(minimum=1, value=50, maximum=100, step=1,
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
    demo.launch(auth=("sntUser", "snt2024Passw"), server_name="0.0.0.0", server_port=5000)
