import re
import subprocess as sp


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


def split_document(file_path):
    lines_french = []
    lines_ducth = []
    pattern_head_of_page = r'\d\-\d+\s\/\sp\.\s\d'
    pattern_left = r'.+\s{2,}'
    # pattern_ducth = r'\s{4,}.+'
    page_number = 1
    try:
        with open(file_path, 'r', encoding='utf-8') as file:

            # Read the file line by line
            for i, line in enumerate(file):
                print(page_number)
                if page_number < 2 and get_page_number(line) is not None:
                    page_number = get_page_number(line)
                    continue
                # keeping page number
                if re.search(pattern_head_of_page, line):
                    lines_french.append(line)
                    lines_ducth.append(line)
                    continue
                # keeping left-line text
                if re.search(pattern_left, line):
                    line_2_add = re.search(pattern_left, line).group()
                else:
                    line_2_add = line
                lines_french.append(line_2_add)
                lines_ducth.append(remove_substring(line, line_2_add))
    except FileNotFoundError:
        print("The specified file was not found.")
    except Exception as e:
        print("An error occurred while reading the file:", str(e))
    return '\n'.join(lines_french), ''.join(lines_ducth)


def get_page_number(line):
    pattern_head_of_page = r'\d\-\d+\s\/\sp\.\s\d'
    if re.search(pattern_head_of_page, line):
        return line
    return None


french_text, dutch_text = split_document('extracted/5-150.txt')
print(french_text)

