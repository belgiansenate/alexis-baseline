from pypdf import PdfReader
from pypdf.generic import DictionaryObject


class Document:
    def __init__(self, french_text, dutch_text, reader: DictionaryObject):
        self.metadata = reader
        self.french_text = french_text
        self.dutch_text = dutch_text

    def __str__(self):
        return f"Document: {self.metadata}"
