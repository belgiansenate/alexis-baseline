import argparse
import logging

from global_variables import *


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--path', type=str, default='Annals_datas.xlsx')
    parser.add_argument('--mode', type=str, default=Mode.local)
    parser.add_argument('--host', type=str, default=host)
    parser.add_argument('--port', type=int, default=port_number)
    parser.add_argument('--collection', type=str, nargs='+', default=[collection_name_bge, collection_name_all_mini])
    parser.add_argument('--embedding', type=str, nargs='+', default=[embedder, embeddings_all_MiniLM_L6_V2])
    logging.captureWarnings(True)
    return parser.parse_args()


