from os import listdir
from os.path import isfile, join


def get_documents_from_folder(folder_path):
    """
    This function returns the list of documents in a folder
    :param folder_path: path to the folder
    :return: contains the list of documents in a folder
    """
    documents = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    return documents
