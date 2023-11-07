from typing import List


class PassageObject:
    def __init__(self,  document_id, document_title, passage_title, page, passage_text):
        self.passage_text = passage_text
        self.passage_title = passage_title
        self.document_title = document_title
        self.metadata = {'document_id': document_id, 'page': page}

    def __str__(self):
        return (f'PassageObject: {self.passage_title}, from document {self.metadata["document_id"]},'
                f' on page {self.metadata["page"]}, text: {self.passage_text}'
                )

