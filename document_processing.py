import re
import subprocess as sp
from os import listdir
from os.path import isfile, join
from pypdf import PdfReader
from passage_object import PassageObject
from document_object import Document

"""
    This file contains utility functions that are used in the main script.
"""


def get_documents_from_folder(folder_path):
    """
    This function returns the list of documents in a folder
    :param folder_path: path to the folder
    :return: contains the list of documents in a folder
    """
    documents = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return documents


def get_document_metadata(document_file_path):
    """
    This function returns the metadata of a document
    :param document_file_path: path to the document
    :return: metadata of a document
    """
    reader = PdfReader(document_file_path)
    return reader.metadata


def transform_pdf_2_txt(path, output_file):
    """
    This function transforms a pdf file to a text file using pdftotext and poppler
    :param path: path to the pdf file
    :param output_file: path to the output (need to be a .txt file)
    :return: None
    """
    # Generate a text rendering of a PDF file in the form of a list of lines.
    args = ['pdftotext', '-layout', path, output_file]
    cp = sp.run(
        args, stdout=sp.PIPE, stderr=sp.DEVNULL,
        check=True, text=True
    )


def split_document(text_files_path):
    """
    This function splits a document into two parts: the left part and the right part
    :param text_files_path: path to the text file .txt following the transformation of the pdf file
    :return: left part and right part of the document
    """
    left_text = []
    right_text = []

    # 2-285 / p. 4     Sénat de Belgique - Séances plénières - Jeudi 3 avril 2003 - Séance du soir - Annales
    pattern_head_of_page = r'\d-\d+\s/\sp\.\s\d+'

    # match left text when it is more than 3 spaces(the right text is always less than 3 spaces)
    pattern_left_text = r'.+\s{3,}'

    # if the first pattern head of page is encountered then the first page is passed we can start to extract the text
    first_page_encountered = False

    try:
        with open(text_files_path, 'r', encoding='utf-8') as file:
            for line in file:
                if re.search(pattern_head_of_page, line):
                    continue

                if re.search(r'\b(Sommaire|Inhoudsopgave)\b', line) or re.search(r'\b(Bijlage|Annexe)\b', line):
                    first_page_encountered = True
                    continue

                if first_page_encountered:
                    match_left_text = re.search(pattern_left_text, line)
                    line_2_add = match_left_text.group() if match_left_text else line
                    dutch_line = line.replace(line_2_add, '').strip()
                    # remove extra spaces
                    line_2_add = re.sub(' +', ' ', line_2_add)
                    dutch_line = re.sub(' +', ' ', dutch_line)

                    ##remove if it only white spaces
                    if line_2_add.strip() != '':
                        left_text.append(line_2_add)

                    if dutch_line.strip() != '' or dutch_line.strip() != '\n':
                        right_text.append(dutch_line)

    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print("An error occurred while reading the file:", str(e))

    return '\n'.join(left_text), '\n'.join(right_text)


def build_document_object(document_file_path, pdf_folder_path, text_folder_path):
    """
    This function builds a document object
    :param document_file_path: path to the document
    :param pdf_folder_path: path to the folder containing the pdf documents
    :param text_folder_path: path to the folder containing the extracted text documents
    :return:  object
    """
    input_file = f'{pdf_folder_path}/{document_file_path}'
    # get document metadata
    metadata = get_document_metadata(f'{input_file}')
    name = metadata['/Title'] + '.txt'
    output_file = f'{text_folder_path}/{name}'
    transform_pdf_2_txt(input_file, output_file)

    # get document text in French and Dutch
    if int(metadata['/Title'][0]) % 2 == 0:
        dutch_text, french_text = split_document(output_file)
    else:
        french_text, dutch_text = split_document(output_file)

    return Document(french_text, dutch_text, metadata)


def count_contents_title(text):
    """
    This function counts the number of contents titles in a text
    :param text: to be processed
    :return: list of contents titles end check points
    """
    pattern_summary = r'\.{2}.\d'  # Example: content.....1 or content.....2 in a single line
    text = text.split('\n')
    check_points = []
    for line in text:
        if re.search(pattern_summary, line):
            check_points.append(line)
    return check_points


def get_summary_titles(text, check_points):
    """
    This function returns the summary titles
    :param text: processed text
    :param check_points: list of contents titles end check points
    :return: list of summary titles
    """
    counter = 0
    contents_counter = len(check_points)
    all_contents, content = [], []
    text = text.split('\n')

    for line in text:
        if counter == contents_counter:
            return all_contents

        content.append(line)
        if line in check_points:
            # join content and add to all_contents

            cont = ' '.join(content)
            # remove '\n' from each content
            all_contents.append(cont)
            content = []
            counter += 1
    return all_contents


def clean_text(text):
    """
    This function cleans the text by removing extra spaces and empty lines
    :param text: processed text
    :return: cleaned text
    """
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)


def remove_chunks(text, chunks, replace_with='\n'):
    """
    This function removes chunks from a text
    :param replace_with: replace the chunk with this string
    :param text: processed text
    :param chunks: chunks to be removed
    :return: text without the chunk
    """
    for chunks in chunks:
        text = text.replace(chunks, replace_with)
    return text.strip()


def build_custom_pattern(pattern):
    """
    This function builds a custom pattern
    :param pattern: match all special characters in a pattern
    :return: return the pattern with special characters escaped by \
    """
    # if patter contains special characters by \ before them
    pattern = re.sub(r'([^\w\s])', r'\\\1', pattern)
    return pattern


def match_pattern_with_position(pattern, chunk, verbose=False):
    """
    This function returns the match, start index and end index of a pattern in a chunk
    :param pattern: a pattern to be matched
    :param chunk: a chunk to be processed
    :param verbose: if True print the pattern, the match and the length of the chunk
    :return: match, start index and end index of a pattern in a chunk
    """
    # remove starting and ending spaces
    result = re.search(pattern, chunk)
    if verbose:
        print(pattern, result, len(chunk))
    if result is None:
        return None, -1, -1

    start_index = result.span()[0]
    end_index = result.span()[1]

    return result.group(0), start_index, end_index


def preprocess_content(content):
    """
    This function preprocesses the content by removing the page number and the extra spaces
    :return: content and page number
    """
    noised_page_number, _, _ = match_pattern_with_position(r'\.{2,}.\d+', content)
    content = content.replace(noised_page_number, '')
    page_number, _, _ = match_pattern_with_position(r'\d+', noised_page_number)
    content = content.strip()
    return content, page_number if page_number else None


def join_lines(string):
    """
    This function joins lines that end with - with '' and join other lines with a space, the reason is that in some
    contents titles or words when the line is too long it is split into two lines
    :param string: to be processed
    :return: result of joining lines
    """
    lines = string.split('\n')
    joined_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.endswith('-'):
            if i + 1 < len(lines):
                line = line + lines[i + 1]
                i += 1  # Skip the next line
        joined_lines.append(line)
        i += 1

    return ' '.join(joined_lines)


def retrieve_chunks_from_document(full_text_cleaned, contents_titles, document_title=None, document_id=None):
    """
    This function retrieves the chunks from a document and returns the passages objects containing all the
    information about the passage :param full_text_cleaned: :param contents_titles:
    :param contents_titles: list of contents titles in the current document
    :param full_text_cleaned: the full text of the document cleaned
    :param document_title: document title
    :param document_id: document id
    :return: passages objects and contents not found (if any error occurred especially for debugging)
    """
    passages = []
    contents_not_found = []
    cleaned_contents_titles = [preprocess_content(content) for content in contents_titles]

    for i, title in enumerate(cleaned_contents_titles):
        full_text_cleaned = full_text_cleaned.strip()
        pattern_for_current_title = build_custom_pattern(title[0])

        pattern_for_following_title = (
            build_custom_pattern(cleaned_contents_titles[i + 1][0])
        ) if i < len(cleaned_contents_titles) - 1 else None

        _, current_content_start_pos, current_content_end_pos = match_pattern_with_position(pattern_for_current_title,
                                                                                            full_text_cleaned)

        if current_content_start_pos == -1 or current_content_end_pos == -1:
            contents_not_found.append(f'No match found for {pattern_for_current_title} for document {document_title}')
            continue

        if pattern_for_following_title is None:
            passage_text = full_text_cleaned[current_content_end_pos:]

        else:
            _, next_content_start_index, _ = match_pattern_with_position(pattern_for_following_title, full_text_cleaned)
            if next_content_start_index == -1:
                contents_not_found.append(
                    f'No match found for {pattern_for_current_title} for document {document_title}')
                continue
            passage_text = full_text_cleaned[current_content_end_pos:next_content_start_index]

            # dropping the passage from the full text by slicing
            full_text_cleaned = full_text_cleaned[next_content_start_index:]

        passage_object = PassageObject(document_id, document_title, title[0], title[1], passage_text)
        passages.append(passage_object)

    return passages, contents_not_found


def preprocess_text(text):
    """
    This function preprocesses the text by removing the contents titles and the extra spaces to be ready for the retrieval
    :param text: to be processed
    :return: cleaned text and summary titles
    """
    text = clean_text(text)
    check_points = count_contents_title(text)
    summary_titles = get_summary_titles(text, check_points)
    text = join_lines(text)
    full_text_cleaned = remove_chunks(text, summary_titles)
    return full_text_cleaned, summary_titles


def build_passages_objects(document_file_path, pdf_folder_path, text_folder_path):
    """
    This function builds the passages objects from a document
    :param document_file_path: path to the document
    :param pdf_folder_path: path to the folder containing the pdf documents
    :param text_folder_path: path to the folder containing the extracted text documents
    :return: passages objects and contents not found (if any error occurred especially for debugging)
    """
    input_file = f'{pdf_folder_path}/{document_file_path}'
    pattern_for_document_id = r'\d+\-\d+'  # Example: 2-285, 6-1, 5-2

    # get document metadata
    metadata = get_document_metadata(f'{input_file}')
    document_title = metadata['/Title']

    # retrieve the document id
    document_id = match_pattern_with_position(
        pattern_for_document_id, document_title
    )[0]  # Example: 2-285, 6-1, 5-2

    legislature_number = int(document_id[0])

    # transform pdf to text with output name = document title.txt
    output_name = document_title + '.txt'
    output_file = f'{text_folder_path}/{output_name}'
    transform_pdf_2_txt(input_file, output_file)

    # if legislature is odd then the first page is in French else it is in Dutch
    if int(legislature_number) % 2 == 0:
        dutch_text, french_text = split_document(output_file)
    else:
        french_text, dutch_text = split_document(output_file)

    # preprocessing text
    french_text, french_contents_titles = preprocess_text(french_text)
    dutch_text, dutch_contents_titles = preprocess_text(dutch_text)

    # build passages objects and return them with the contents not found
    french_passages_objects, contents_not_found_french = retrieve_chunks_from_document(
        french_text, french_contents_titles, document_title, document_id
    )
    dutch_passages_objects, contents_not_found_dutch = retrieve_chunks_from_document(
        dutch_text, dutch_contents_titles, document_title, document_id
    )

    return french_passages_objects, dutch_passages_objects, contents_not_found_french, contents_not_found_dutch


build_passages_objects('webdriver-4.pdf', 'documents', 'extracted')
