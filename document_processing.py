"""
    This file contains utility functions that are used to chunk all annals files from 2000 to nowadays.
"""

import logging
import os
import re
import subprocess as sp
from pdf_object import PdfObject
import pandas as pd
import requests

from passage_object import PassageObject

def transform_pdf_2_txt(path, output_file):
    """
        This function transforms a pdf file to a text file using pdftotext and poppler
        :param path: path to the pdf file
        :param output_file: path to the output (need to be a .txt file)
        :return: None
    """
    # Generate a text rendering of a PDF file in the form of a list of lines.
    args = ['pdftotext', '-layout', path, output_file]
    try:
        sp.run(args, stdout=sp.PIPE, stderr=sp.DEVNULL, check=True, text=True)
    except sp.CalledProcessError as e:
        print(f'Error: {e}')
        print(f'Error output: {e.output}')


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

    pattern = r'^(Bijlage\s+Annexe|Annexe\s+Bijlage)$'
    # Compile the regex pattern
    regex = re.compile(pattern)
    # if the first pattern head of page is encountered then the first page is passed we can start to extract the text
    first_page_encountered = False
    first_occ = True

    try:
        with open(text_files_path, 'r', encoding='utf-8') as file:
            for line in file:
                if re.search(pattern_head_of_page, line):
                    continue

                if regex.match(line.strip()):
                    # If it does, check if it's not the first occurrence
                    if "Bijlage" in line.strip() and "Annexe" in line.strip() and first_occ:
                        # If it's not the first occurrence, print the line and break the loop
                        first_occ = False
                        continue
                    else:
                        # If it's the first occurrence, set the flag to False
                        #print(line.strip())
                        break

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
                        if line_2_add.strip() == 'o' or line_2_add.strip() == 'e' or line_2_add.strip() == "er" or line_2_add.strip() == "os" or line_2_add.strip() == "ste":
                            continue
                        else:
                            left_text.append(line_2_add)

                    if dutch_line.strip() != '' or dutch_line.strip() != '\n':
                        if dutch_line.strip() == 'o' or dutch_line.strip() == 'e' or dutch_line.strip() == "er" or dutch_line.strip() == "os" or dutch_line.strip() == "ste":
                            continue
                        else:
                            right_text.append(dutch_line)

    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print("An error occurred while reading the file:", str(e))

    return '\n'.join(left_text), '\n'.join(right_text)


def is_matching(string, patterns):
    """
        Checks if a particular string matches a list of patterns
        :param string: the string to be processed
        :param patterns: the patterns to match
        :return: a Boolean
    """
    return any(re.search(pattern, string) for pattern in patterns)


def count_contents_title(text):
    """
        This function counts the number of contents titles in a text
        :param text: to be processed
        :return: list of contents titles end check points
    """
    # Example: content.....1 or content.....2 in a single line
    pattern_summary = [r'\.{2}p\.\s\d', r'\.{2}.\d', r'\.{2}\sp\.\s\d', r'p\.\s\d']
    pattern_not_to_match = [r',\s(p|pp)\.\s\d+', r'\(?p\.\s\d+\)?']
    text = text.split('\n')
    check_points = []
    for line in text:
        if is_matching(line, pattern_not_to_match):
            continue
        elif is_matching(line, pattern_summary):
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
        if line == "":
            continue
        if counter == contents_counter:
            return all_contents

        content.append(line)
        content = [line.strip() for line in content]
        if line in check_points:
            for i in range(len(content)):
                line = content[i]
                if not(line.endswith('-')):
                    content[i] += " "
            # join content and add to all_contents
            #print(content)
            cont = ''.join(content)
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
    replacements = {
        '’': "'",
        'Ŕ': '–',
        '‟': "'",
        '„': '‘'
    }

    for old, new in replacements.items():
        text = text.replace(old, new)
        
    patterns_and_replacements = [
        (r'(no|n o|nos|Nos|N) (\d+)', r'n \2'), (r'(\d+)(er|e)', r'\1'), (r'(§?)(\d+)(,)', r'\1\2 \3'),
        (r'(\w+)\s*[–-]\s*(\w+)', r'\1-\2'), (r'(\d+)(ste)', r'\1'), (r'([^;]+) ;', r'\1;'), (r'(ème)\s+(\d+)', r'\2\1')
    ]
    modified_text = text
    for pattern, replacement_func in patterns_and_replacements:
        modified_text = re.sub(pattern, replacement_func, modified_text)

    lines = modified_text.split('\n')
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
    extra_pattern = [r'\.{2,}p\.\s\d+', r'\.{2,}\sp\.\s\d+', r'p\.\s\d+']
    if is_matching(content, extra_pattern):
        for pattern in extra_pattern:
            noised_page_number, _, _ = match_pattern_with_position(pattern, content)
            if noised_page_number:
                content = content.replace(noised_page_number, '')
                noised_page_number = noised_page_number.replace('p', '')
                break
    else:
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
        if line.endswith('-') or line.endswith('–'):
            if i + 1 < len(lines):
                line = line + lines[i + 1]
                i += 1  # Skip the next line
        joined_lines.append(line)
        i += 1

    return ' '.join(joined_lines)


def get_chunks_from_text(full_text_cleaned, contents_titles, document_id=None, pub_date=None, language=None, legislature=None, num_legislature=None):
    """
        This function retrieves the chunks from a document and returns the passages objects containing all the
        information about the passage
        :param num_legislature: the number of the document within that particular legislature
        :param legislature: the legislature
        :param language: chunk language
        :param pub_date: date
        :param contents_titles: list of contents titles in the current document
        :param full_text_cleaned: the full text of the document cleaned
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
            contents_not_found.append(f'No match found for {pattern_for_current_title} for document {document_id}')
            continue

        if pattern_for_following_title is None:
            passage_text = full_text_cleaned[current_content_end_pos:]

        else:
            _, next_content_start_index, _ = match_pattern_with_position(pattern_for_following_title, full_text_cleaned)
            if next_content_start_index == -1:
                contents_not_found.append(
                    f'No match found for {pattern_for_current_title} for document {document_id}')
                continue
            passage_text = full_text_cleaned[current_content_end_pos:next_content_start_index]

            # dropping the passage from the full text by slicing
            full_text_cleaned = full_text_cleaned[next_content_start_index:]

        passage_object = PassageObject(document_id, title[0], title[1], pub_date, passage_text, language, legislature, num_legislature)
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


def download_pdf_from_website(link, path):
    """
        This function downloads a file from a link
        :param link: hyperlink to the file
        :param path: path to the folder where the file will be saved
        :return: None
    """
    try:
        # avoid ssl certificate error
        r = requests.get(link, verify=False)
        logging.captureWarnings(True)
        open(path, 'wb').write(r.content)
    except Exception as e:
        print(f'Error: {e}')


def remove_empty_passages(passages_objects):
    """
        This function removes empty passages from a list of passages objects
        :param passages_objects: list of passages objects
        :return: list of passages objects without empty passages
    """
    return [passage_object for passage_object in passages_objects if passage_object.page_content.strip() != '']


def build_passages_objects(pdf_object: PdfObject):
    """
        This function builds the passages objects from a document
        :param pdf_object: pdf object containing the document information
        :return: passages objects and contents not found (if any error occurred especially for debugging)
    """
    pdf_file = pdf_object.id + '.pdf'

    # download pdf file from the website to the local path it's a provisional solution because the network doesn't
    # allow it caused by ssl certificate
    download_pdf_from_website(pdf_object.hyperlink, pdf_file)

    # transform pdf to text with output name = document title.txt
    text_file = pdf_object.id + '.txt'

    transform_pdf_2_txt(pdf_file, text_file)
    # transform_pdf_2_txt(pdf_object.hyperlink, output_file_path)

    # if legislature is odd then the first page is in French else it is in Dutch
    if int(pdf_object.legislature) % 2 == 0:
        dutch_text, french_text = split_document(text_file)
    else:
        french_text, dutch_text = split_document(text_file)

    # preprocessing text
    french_text, french_contents_titles = preprocess_text(french_text)
    dutch_text, dutch_contents_titles = preprocess_text(dutch_text)

    # build passages objects and return them with the contents not found
    french_passages_objects, contents_not_found_french = get_chunks_from_text(
        french_text, french_contents_titles, pdf_object.id, pdf_object.date, language='fr',
        legislature=pdf_object.legislature, num_legislature=pdf_object.num
    )
    dutch_passages_objects, contents_not_found_dutch = get_chunks_from_text(
        dutch_text, dutch_contents_titles, pdf_object.id, pdf_object.date, language='nl',
        legislature=pdf_object.legislature, num_legislature=pdf_object.num
    )

    # drop the pdf file and the text file to save space
    os.remove(pdf_file)
    os.remove(text_file)

    return french_passages_objects, dutch_passages_objects, contents_not_found_french, contents_not_found_dutch


def build_pdf_object_via_hyperlink(path_to_excel_file,
                                   hyperlink="https://www.senate.be/www/webdriver?MItabObj=pdf&MIcolObj=pdf"
                                             "&MInamObj=pdfid&MItypeObj=application/pdf&MIvalObj=", limit=None):
    """
        This function returns the records from the database
        :param limit: limit the number of records to be returned
        :param hyperlink: hyperlink is the path to document  (hyperlink + document_id)
        :param path_to_excel_file: path to the Excel file containing the records
        :return: a list of pdf objects
    """
    df = pd.read_excel(path_to_excel_file)
    records = df.to_dict('records')
    pdf_objects = []
    for i, document in enumerate(records):
        if limit and i == limit:
            break
        pdf_object = PdfObject(document['pdfid'], document['handelingenid'], document['datum'],
                               document['legislatuur'], document['nummer'], document['beginblz'],
                               document['eindblz'], hyperlink)
        pdf_objects.append(pdf_object)

    return pdf_objects
