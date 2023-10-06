class Document:
    def __init__(self, french_text, dutch_text, doc_number, date, title, author, publisher, pages):
        self.doc_number = doc_number
        self.date = date
        self.title = title
        self.author = author
        self.publisher = publisher
        self.pages = pages
        self.french_text = french_text
        self.dutch_text = dutch_text
