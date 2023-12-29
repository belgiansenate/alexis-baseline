import csv
import re
import time
import os
import gradio as gr
from datetime import datetime
from arguments import parse_args
from database_operations import querying_to_db
from vector_database_manager import ChromaClient, Mode

from llama_cpp import Llama


args = parse_args()
if args.mode == Mode.local:
    client = ChromaClient(mode=Mode.local, path_directory='chromadb')
    print(f"collection contains : {client.get_collection(args.collection).count()} vectors")
else:
    client = ChromaClient(host=args.host, mode=Mode.host, port_number=args.port)
    client.get_or_create_collection(args.collection)


def build_prompt(query, contexts, language="fr"):
    """
    Build the prompt to be used in the generation
    :param query:  question
    :param contexts: set of contexts related to the question and retrieved from the database
    :param language: language of the question
    :return: prompt
    """
    if language == "nl":
        return (f"Beantwoord de vraag aan de hand van de gegeven context. Je antwoord moet in je eigen woorden zijn. "
                f"\n\n Context: {contexts} \n\n Vraag: {query} \n\n Antwoord:"),
    elif language == "fr":
        return (f"Réponds à la question en utilisant le contexte donné. Ta réponse doit être rédigée dans tes propres "
                f"mots. {query}\nContexte: {contexts}\n Réponse:")
    else:
        raise ValueError("Language not supported")

def date_printing(date):
    date_format = '%Y-%m-%d %H:%M:%S'
    return ((datetime.strptime(date, date_format)).date()).strftime("%d/%m/%Y")
def answer_concat(texts, metadata):
    """
    Concatenate the results to be displayed
    :param texts: texts to be concatenated
    :param metadata: metadata to be concatenated
    :return:   results
    """
    results = []
    date_format = '%Y-%m-%d %H:%M:%S'
    for i, text in enumerate(texts):
        results.append(
            f'Source {i + 1}({metadata[i]["leg_title"]}, du {((datetime.strptime(metadata[i]["date"], date_format)).date()).strftime("%d/%m/%Y")}, titre : {metadata[i]["passage_title"]}, p.{metadata[i]["page"]}) \n {text}')

    return '\n'.join(results)


# remove all special characters
drop_special_char = lambda x: re.sub(r'[\n\r\t;,:!?()\[\]{}=+\-*/\\]', '', x)


def save_to_csv(question, context, answer):
    """
    Save the question, context and answer to a csv file
    :param question: question
    :param context: context
    :param answer:  answer
    :return: None
    """
    if question == "" or context == "" or answer == "":
        gr.Warning("Please fill all the fields")
        return

    with open('datas.csv', mode='a+', newline="", encoding="utf8") as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([drop_special_char(question), drop_special_char(context), drop_special_char(answer)])
    gr.Info("Saved to csv")


def retrieve_from_vector_db(message, n_results):
    try:
        results = querying_to_db(chroma_client=client, collection_name=args.collection, nl_query=message,
                                 embedding_model=args.embedding, n_results=n_results)
    except Exception as e:
        print(e)
        return "Sorry, I couldn't find any answer to your question", message
    documents = results['documents']
    metadatas = results['metadatas']
    distances =results['distances']
    # error : File name too long
    return documents[0], metadatas[0], answer_concat(documents[0], metadatas[0])


def echo_chunks(message, chat_history, n_result=1):
    _, _, bot_message = retrieve_from_vector_db(message, n_result)
    chat_history.append((message, bot_message))
    time.sleep(2)
    return "", chat_history


# TODO add generation
# TODO: What if we change the question ? need to change sources
# TODO: add links into pdf files.
# TODO: Work on with the history.
def slow_echo(message, history, prompt, n_results=1, temperature=0.1, top_p=0.5, max_new_tokens=300):
    _, metadatas, bot_message = retrieve_from_vector_db(message, n_results)

    llm = Llama(model_path="Models/zephyr-7b-beta.Q4_K_M.gguf", n_ctx=32000, n_batch=3)

    input_text = ""
    if metadatas[0]["language"] == 'fr':
        input_text = f""" use the following context to answer the question. If you do not know the answer, 
        just say that you do not know. Answer in French. Give details and source from where you get the answer.
        
        {bot_message}
    
        Question: {message}
        Answer:
        Source: Give the source here.
        """
    elif metadatas[0]["language"] == 'nl':
        input_text = f""" use the following context to answer the question. If you do not know the answer, 
        just say that you do not know. Answer in Dutch. Give details.

        {bot_message}

        Question: {message}
        Answer:
        Source: Give the source here.
        """

    input_prompt = f"""<|system|>
    You are a chatbot who always responds in the style of a lawyer. 
    </s>
    <|user|>
    {input_text}
    </s>
    <|assistant|>"""

    output = llm(
        input_prompt,
        max_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        echo=False,
        stop=["#"],
    )
    output_text = output['choices'][0]["text"].strip()
    print(output_text)
    for i in range(len(output_text)):
        time.sleep(0.01)
        yield output_text[:i + 1]
#css = """
##chatbot{
#background: #E3F2FD;
#}
#accordion {
#background: #E3F2FD;
#}
#"""
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
                save_button = gr.Button(value="Save to CSV")
                gr.ClearButton([question, context, answer], value="Clear All")
    save_button.click(save_to_csv, [question, context, answer])
    msg.submit(echo_chunks, [msg, chatbot, n_results], [msg, chatbot])

    with gr.Tab("generation"):
        chatbot = gr.Chatbot(label="Sen Chatbot", show_label=True, container=True, render=False,
                             height=400
                             )
        gr.ChatInterface(slow_echo,
                         chatbot=chatbot,
                         additional_inputs=[
                             gr.Textbox(placeholder="fill the prompt", label="prompt", scale=2, render=False),
                             gr.Slider(minimum=1, maximum=10, step=1, label="n_results", info="Number of relevant passages to be used", scale=1, render=False),
                             gr.Slider(minimum=0, maximum=1, step=0.05, label="temperature", info="Value used to modulate the next token probabilities", scale=1, render=False),
                             gr.Slider(minimum=0, maximum=1, step=0.1, label="top_p", info="A probability threshold for generating the output. If < 1.0, only keep the top tokens with cumulative probability >= top_p (nucleus filtering)", scale=1, render=False),
                             gr.Slider(minimum=0, maximum=512, step=8, label="max_new_tokens", info="The maximum number of tokens the model should generate as output", scale=1, render=False)
                         ],
                         additional_inputs_accordion=gr.Accordion("Advanced settings", open=False, render=False)
                         )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
