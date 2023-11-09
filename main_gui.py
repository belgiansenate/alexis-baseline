import csv
import json
import os.path
import re

import gradio as gr
import random
import time

from sentence_transformers import SentenceTransformer

from document_retrieving_for_chroma import processing_storing_to_db, querying_to_db
from embedding_function import SentenceBERTEmbedding
from vector_database_manager import ChromaClient, Mode

embedder = SentenceBERTEmbedding()
collection_name = "test_collection_2"
client = ChromaClient(mode=Mode.local, path_directory='chromadb')
collection = client.get_or_create_collection(collection_name)


# processing_storing_to_db(path_to_pdf_folder='documents', path_to_text_folder='extracted',
#                          chromadb_client=client, collection_name=collection_name, embedding_function=embedder)

def answer_concat(texts):
    results = []
    for i, text in enumerate(texts):
        results.append(f'\033[1m Result\033[0m {i + 1}: \n {text}')

    return '\n'.join(results)


def respond(message, chat_history, n_results):
    results = querying_to_db(chroma_client=client, collection_name=collection_name, nl_query=message,
                             embedding_model=embedder, n_results=n_results)
    documents = results['documents']
    # error : File name too long
    bot_message = answer_concat(documents[0])
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


# remove all special characters
drop_special_char = lambda x: re.sub(r'[\n\r\t;,:!?()\[\]{}=+\-*/\\]', ' ', x)


def save_to_json(question, context, answer):
    data = [{
        "question": drop_special_char(question),
        "context": drop_special_char(context),
        "answer": drop_special_char(answer)
    }]
    with open('datas.csv', mode='a+', newline="", encoding="utf8") as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([drop_special_char(question), drop_special_char(context), drop_special_char(answer)])
    print("Csv file saved")


with gr.Blocks() as demo:
    with gr.Tab("retrieval"):
        with gr.Group():
            chatbot = gr.Chatbot(show_copy_button=True, layout="bubble", bubble_full_width=False)
            with gr.Row():
                msg = gr.Textbox()
                n_results = gr.Slider(minimum=1, maximum=10, step=1, label="Number of results")
                with gr.Column(min_width=50):
                    clear_input_space = gr.ClearButton([msg], value="Clear Input")
                    clear = gr.ClearButton([msg, chatbot, n_results], value="Clear All")
        with gr.Group(visible=True):
            with gr.Row():
                question = gr.Textbox(label="Question")
                context = gr.Textbox(label="Context")
                answer = gr.Textbox(label="Answer")
            save_button = gr.Button(value="Save to Json")
    with gr.Tab("generation"):
        pass
    save_button.click(save_to_json, [question, context, answer], trigger_mode="once")
    msg.submit(respond, [msg, chatbot, n_results], [msg, chatbot])

demo.launch()
