class PassageObject:
    def __init__(self, document_id, passage_title, page, date,  passage_text, language):
        self.passage_text = 'Titre : ' + passage_title + ' : ' + passage_text
        self.metadata = {'document_id': document_id,
                         'page': page,
                         'date': date,
                         'passage_title': passage_title,
                         'language': language
                         }

    def __str__(self):
        return (f'PassageObject: {self.metadata["passage_title"]}'
                f' on page {self.metadata["page"]}, at date {self.metadata["date"]} ,text: {self.passage_text}'
                )


