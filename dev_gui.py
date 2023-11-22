import csv
import re
import time
from random import random
import transformers
import gradio as gr
from database_operations import querying_to_db, passages_storing
from models import SentenceBERTEmbedding
from vector_database_manager import ChromaClient, Mode

embedder = SentenceBERTEmbedding()
model = transformers.AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
collection_name = "test_collection_2"
client = ChromaClient(mode=Mode.local, path_directory='chromadb')
collection = client.get_or_create_collection(collection_name)

##################uncomment this to process and store the documents in the database###################
passages_storing('Annals_datas.xlsx',
                 chromadb_client=client, collection_name=collection_name, embedding_function=embedder)


def build_prompt(query, contexts, language="fr"):
    if language == "de":
        return (f"Beantwoord de vraag aan de hand van de gegeven context. Je antwoord moet in je eigen woorden zijn. "
                f"\n\n Context: {contexts} \n\n Vraag: {query} \n\n Antwoord:"),
    elif language == "fr":
        return (f"Réponds à la question en utilisant le contexte donné. Ta réponse doit être rédigée dans tes propres "
                f"mots. {query}\nContexte: {contexts}\n Réponse:")
    else:
        raise ValueError("Language not supported")


def answer_concat(texts, metadatas):
    results = []
    for i, text in enumerate(texts):
        results.append(
            f'Result {i + 1}( Document ID : {metadatas[i]["document_id"]} === Title : {metadatas[i]["passage_title"]} === Page: {metadatas[i]["page"]}) \n {text}')

    return '\n'.join(results)


# remove all special characters
drop_special_char = lambda x: re.sub(r'[\n\r\t;,:!?()\[\]{}=+\-*/\\]', '', x)


def save_to_csv(question, context, answer):
    if question == "" or context == "" or answer == "":
        gr.Warning("Please fill all the fields")
        return

    with open('datas.csv', mode='a+', newline="", encoding="utf8") as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([drop_special_char(question), drop_special_char(context), drop_special_char(answer)])
    gr.Info("Saved to csv")


def retrieve_from_vector_db(message, n_results=1):
    try:
        results = querying_to_db(chroma_client=client, collection_name=collection_name, nl_query=message,
                                 embedding_model=embedder, n_results=n_results)
    except Exception as e:
        print(e)
        return "Sorry, I couldn't find any answer to your question", message
    documents = results['documents']
    metadatas = results['metadatas']
    # error : File name too long
    return answer_concat(documents[0], metadatas[0])


def echo_chunks(message, chat_history, n_result=1):
    bot_message = retrieve_from_vector_db(message, n_result)
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


def slow_echo(message, history, prompt, n_results=1):
    bot_message = retrieve_from_vector_db(message, n_results)
    print(history)
    for i in range(len(bot_message)):
        time.sleep(0.01)
        yield bot_message[:i + 1]


with gr.Blocks() as demo:
    with gr.Tab("retrieval"):
        with gr.Group():
            chatbot = gr.Chatbot(show_copy_button=True, layout="bubble", bubble_full_width=False)
            with gr.Row():
                msg = gr.Textbox(label="Question")
                n_results = gr.Slider(minimum=1, maximum=10, step=1, label="Number of results")
                with gr.Column(min_width=50):
                    clear_input_space = gr.ClearButton([msg], value="Clear Input")
                    clear = gr.ClearButton([msg, chatbot, n_results], value="Clear All")
        with gr.Group():
            with gr.Row():
                question = gr.Textbox(label="Question")
                context = gr.Textbox(label="Context")
                answer = gr.Textbox(label="Answer")
            with gr.Row():
                save_button = gr.Button(value="Save to Json")
                gr.ClearButton([question, context, answer], value="Clear All")
    save_button.click(save_to_csv, [question, context, answer])
    msg.submit(echo_chunks, [msg, chatbot, n_results], [msg, chatbot])

    with gr.Tab("generation2"):
        gr.ChatInterface(slow_echo,
                         additional_inputs=[
                             gr.Textbox(placeholder="fill the prompt", label="prompt"),
                             gr.Slider(minimum=1, maximum=10, step=1, label="n_results")]
                         )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
