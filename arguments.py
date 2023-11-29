import argparse
import logging
from global_variables import *
from vector_database_manager import Mode


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--path', type=str, default='Annals_datas.xlsx')
    parser.add_argument('--mode', type=str, default=Mode.local)
    parser.add_argument('--host', type=str, default=host)
    parser.add_argument('--port', type=int, default=port_number)
    parser.add_argument('--collection', type=str, default=collection_name)
    parser.add_argument('--embedding', type=str, default=embedder)
    logging.captureWarnings(True)
    return parser.parse_args()



