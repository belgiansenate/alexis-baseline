from typing import List


class PassageObject:
    def __init__(self, passage_id, pages: List[int], document_id, passage_text):
        self.passage_text = passage_text
        self.passage_id = passage_id
        self.metadata = {'document_id': document_id, 'pages': pages}

    def __str__(self):
        return f'PassageObject: {self.passage_id}'
