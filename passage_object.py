class PassageObject:
    def __init__(self, document_id, passage_title, page, passage_text):
        self.passage_text = passage_text
        self.metadata = {'document_id': document_id,
                         'page': page,
                         'passage_title': passage_title,
                         }

    def __str__(self):
        return (f'PassageObject: {self.metadata["passage_title"]}'
                f' on page {self.metadata["page"]}, text: {self.passage_text}'
                )
