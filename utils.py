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
                    continue

                if re.search(r'\b(Sommaire|Inhoudsopgave)\b', line):
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
                        lines_french.append(line_2_add)

                    if dutch_line.strip() != '' or dutch_line.strip() != '\n':
                        lines_dutch.append(dutch_line)


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


def count_contents_title(text):
    pattern_summary = r'\.{2}.\d'
    text = text.split('\n')
    check_points = []
    for line in text:
        if re.search(pattern_summary, line):
            check_points.append(line)
    return check_points


def get_summary_titles(text, check_points):
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
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(cleaned_lines)


def flat_text(text):
    # if line end with a - then use ''.join() and keep the - to join the line with the next one else use ' '.join()
    for line in text.split('\n'):
        line = line.rstrip('-')
        if line.endswith('-'):
            text = text.replace(line, ''.join(line.split('-')))
        else:
            text = text.replace(line, ' '.join(line.split('-')))


def remove_chunks(text, chunks):
    for chunk in chunks:
        text = text.replace(chunk, '\n')
    return text.strip()


def build_custom_pattern(pattern):
    # if patter contains special characters by \ before them
    pattern = re.sub(r'([^\w\s])', r'\\\1', pattern)
    return pattern


def match_pattern(pattern, chunk, verbose=False):
    # remove starting and ending spaces
    result = re.search(pattern, chunk)
    if verbose:
        print(pattern, result, len(chunk))
    if result is None:
        return None, -1, -1

    start_index = result.span()[0]
    end_index = result.span()[1]

    return result.group(0), start_index, end_index


def get_digits(text):
    return re.findall(r'\d+', text)


def preprocess_content(content):
    noised_page_number, _, _ = match_pattern(r'\.{2,}.\d+', content)
    content = content.replace(noised_page_number, '')
    page_number, _, _ = match_pattern(r'\d+', noised_page_number)
    content = content.strip()
    return content, page_number


def join_lines(string):
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


def retrieve_chunks_from_document(full_text_cleaned, contents_titles):
    passages = []
    cleaned_contents_titles = []
    for content in contents_titles:
        preprocess_content(content)
        cleaned_contents_titles.append(preprocess_content(content))

    for i, title in enumerate(cleaned_contents_titles):
        full_text_cleaned = full_text_cleaned.strip()
        # print(len(full_text_cleaned))
        pattern_for_current_title = build_custom_pattern(title[0])

        pattern_for_following_title = build_custom_pattern(cleaned_contents_titles[i + 1][0]) \
            if i < len(cleaned_contents_titles) - 1 else None

        _, current_content_start_pos, current_content_end_pos = match_pattern(pattern_for_current_title,
                                                                              full_text_cleaned)

        if current_content_start_pos == -1 or current_content_end_pos == -1:
            # print(
            #     f'No match found for {pattern_for_current_title} with start index {current_content_start_pos} and end '
            #     f'index {current_content_end_pos} next {pattern_for_following_title}')
            # print(full_text_cleaned)
            continue

        if pattern_for_following_title is None:
            passage = full_text_cleaned[current_content_end_pos:]

        else:
            _, next_content_start_index, _ = match_pattern(pattern_for_following_title, full_text_cleaned)
            passage = full_text_cleaned[current_content_end_pos:next_content_start_index]

            # dropping the passage from the full text by slicing
            full_text_cleaned = full_text_cleaned[next_content_start_index:]

        passages.append(passage)

    return passages

# test on a single document

# french, dutch = split_document('extracted/5-150.txt')
#
# dutch = clean_text(dutch)
#
# check_points = count_contents_title(dutch)
#
# summary_titles = get_summary_titles(dutch, check_points)
#
# text = join_lines(dutch)
# # print(len(text))
#
# full_text_cleaned = remove_chunks(text, summary_titles)
# with open('test.txt', 'w', encoding='utf-8') as file:
#     file.write(full_text_cleaned)
# passages = retrieve_chunks_from_document(full_text_cleaned, summary_titles)
# print(len(passages), len(summary_titles))
