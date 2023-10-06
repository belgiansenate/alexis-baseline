import utils


class PassageEmbeddingObject:
    def __init__(self, passage_id, passage_embedding, pages, document_id):
        self.passage_id = passage_id
        self.passage_embedding = passage_embedding
        self.metadata = utils.build_metadata(document_id, pages)
