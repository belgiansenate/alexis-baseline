from typing import List


class PassageObject:
    def __init__(self, pages: List[int], document_id, passage_text, passage_title):
        self.passage_text = passage_text
        self.passage_title = passage_title
        self.metadata = {'document_id': document_id, 'pages': pages}

    def __str__(self):
        return f'PassageObject: {self.passage_title}'

