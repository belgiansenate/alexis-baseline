import re
import subprocess as sp
from os import listdir
from os.path import isfile, join
from document_object import Document
from pypdf import PdfReader

"""
    This file contains utility functions that are used in the main script.
"""


# get all documents from a folder
def get_documents_from_folder(folder_path):
    documents = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return documents


def get_document_metadata(document_file_path):
    reader = PdfReader(document_file_path)
    return reader.metadata


def transform_pdf_2_txt(path, output_file):
    # Generate a text rendering of a PDF file in the form of a list of lines.
    args = ['pdftotext', '-layout', path, output_file]
    cp = sp.run(
        args, stdout=sp.PIPE, stderr=sp.DEVNULL,
        check=True, text=True
    )
    return cp.stdout


def remove_substring(string, substring):
    return string.replace(substring, "")


def split_document(text_files_path):
    lines_french = []
    lines_dutch = []
    pattern_head_of_page = r'\d-\d+\s/\sp\.\s\d+'
    pattern_left_text = r'.+\s{2,}'
    first_page_encountered = False

    try:
        with open(text_files_path, 'r', encoding='utf-8') as file:
            for line in file:
                if re.search(pattern_head_of_page, line):
                    first_page_encountered = True
                    lines_french.append(line)
                    lines_dutch.append(line)
                    continue

                if first_page_encountered:
                    match_left_text = re.search(pattern_left_text, line)
                    line_2_add = match_left_text.group() if match_left_text else line
                    lines_french.append(line_2_add)
                    lines_dutch.append(line.replace(line_2_add, '').strip())

    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print("An error occurred while reading the file:", str(e))

    return '\n'.join(lines_french), '\n'.join(lines_dutch)


def build_document_object(document_file_path, pdf_folder_path, text_folder_path):
    input_file = f'{pdf_folder_path}/{document_file_path}'
    # get document metadata
    metadata = get_document_metadata(f'{input_file}')
    name = metadata['/Title'] + '.txt'
    output_file = f'{text_folder_path}/{name}'
    transform_pdf_2_txt(input_file, output_file)

    # get document text in French and Dutch
    french_text, dutch_text = split_document(output_file)

    return Document(french_text, dutch_text, metadata)


def get_page_number(line):
    pattern_head_of_page = r'\d\-\d+\s\/\sp\.\s\d'
    if re.search(pattern_head_of_page, line):
        return line
    return None


def get_chunks(text):
    return None