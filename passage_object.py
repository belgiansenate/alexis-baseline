class PassageObject:
    
    def __init__(self, document_id, passage_title, page, date,  passage_text, language, leg, num_leg):
        self.page_content = passage_text
        self.metadata = {'document_id': document_id,
                         'page': page,
                         'date': date,
                         'passage_title': passage_title,
                         'language': language,
                         'leg_title': f"Annale {leg}-{num_leg}"
                         }

    def __str__(self):
        return (f'PassageObject: {self.metadata["passage_title"]}'
                f' on page {self.metadata["page"]}, at date {self.metadata["date"]} ,text: {self.page_content}'
                )


