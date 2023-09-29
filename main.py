import re
import subprocess as sp
def remove_substring(string, substring):
    # Escape any special characters in the substring
    escaped_substring = re.escape(substring)

    # Create the pattern to match the substring
    pattern = r'\b' + escaped_substring + r'\b'  # \b for word boundary

    # Use re.sub to remove the substring
    return re.sub(pattern, '', string)

def pdftotext(path, output_file):
    # Generate a text rendering of a PDF file in the form of a list of lines.
    args = ['pdftotext', '-layout', path, output_file]
    cp = sp.run(
        args, stdout=sp.PIPE, stderr=sp.DEVNULL,
        check=True, text=True
    )
    return cp.stdout


pdftotext('documents/5-150.pdf', 'extracted/5-150.txt')

pattern_head_of_page = r'\d\-\d+\s\/\sp\.\s\d'

pattern_french = r'.+\s{2,}'

file_path = 'extracted/5-150.txt'
lines_french = []
lines_ducth = []
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        # Read the file line by line
        for i, line in enumerate(file):
            if re.search(pattern_head_of_page, line):
                lines_french.append(line)
                lines_ducth.append(line)
                continue
            if re.search(pattern_french, line):
                line_2_add = re.search(pattern_french, line).group()

            else:
                line_2_add = line
            lines_french.append(line_2_add)
            lines_ducth.append(remove_substring(line, line_2_add))
    print(lines_ducth)



except FileNotFoundError:
    print("The specified file was not found.")
except Exception as e:
    print("An error occurred while reading the file:", str(e))



