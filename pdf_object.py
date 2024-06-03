# TODO add author
class PdfObject:
    def __init__(self, pdf_id, act, date, legislature, num, start_page, end_page, link):
        self.id = str(pdf_id)
        self.date = str(date)
        self.act = str(act)
        self.legislature = legislature
        self.num = num
        self.start_page = start_page
        self.end_page = end_page
        self.hyperlink = link + self.id

    def __str__(self):
        return (f'Document_records_object: {self.id}, from document {self.date},'
                f' on page {self.legislature}'
                )