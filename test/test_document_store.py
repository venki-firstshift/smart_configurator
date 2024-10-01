import json

from langchain_community.document_loaders import CSVLoader
from utils import utils
from rag.document_store import DocumentStoreBuilder
import csv
import logging
logging.basicConfig(level=logging.INFO)
import tempfile
import pandas as pd
from pathlib import Path
import os

ENTITY_KEYS = [
    'ENTITY_CATEGORY', 'ENTITY_NAME', 'ENTITY_SOURCE', 'ENTITY_TYPE', 'DIMENSION_SEQUENCE',
    'DIMENSION_TYPE', 'DD1_PK', 'DD2_PK','DD3_PK', 'DD4_PK', 'DD5_PK'
]

def get_input_doc(test_file):
    # tf = tempfile.NamedTemporaryFile("w")
    # tmp_file = tf.name
    # try:
    #     data_df = pd.read_csv(test_file, nrows=100)
    #     data_df.to_csv(tmp_file)
    #     master_loader = CSVLoader(tmp_file)
    #     docs = master_loader.load()
    #     return docs[0].page_content
    # finally:
    #     # remove the temp file
    #     tmp_path = Path(tf.name)
    #     if tmp_path.exists():
    #         os.remove(tmp_file)
    with open(test_file, 'r') as f:
        dict_reader = csv.DictReader(f)
        headers = list(dict_reader.fieldnames)
    # convert headers into a doc
    if 'UU_ID' in headers: headers.remove('UU_ID')
    sorted_headers_str = ','.join(sorted(headers))
    return sorted_headers_str

def discover_entities(retriever):
    data_dir = utils.read_env_variable("TENANT_DATA_DIR", "./test_data/Tenant_Config_Samples")
    while True:
        file_path = input('Give the input file to discover entity(quit to end) : ')
        if file_path == 'quit':
            exit(0)
        test_product_master_file = f"{data_dir}/{file_path}"
        doc_content = get_input_doc(test_product_master_file)
        matches = retriever.invoke(doc_content)
        if matches is not None and len(matches) > 0:
            print(f"Matches : {len(matches)}")
            entity_config = {ek: matches[0].metadata[ek] for ek in ENTITY_KEYS}
            print(json.dumps(entity_config, indent=2))
        else:
            print("There are no matches")


if __name__ == '__main__':
    store_builder = DocumentStoreBuilder()
    # add documents to the builder before building
    tenant_data_paths = ['Std_Data', 'LLF_Data', 'Adient', 'VictoriaSecret']
    for tenant_data_path in tenant_data_paths:
        logging.info(f"Loading data from {tenant_data_path}")
        store_builder.add_tenant_entity_data(tenant_data_path)
    retriever = store_builder.build_store_as_retriever()
    discover_entities(retriever)

#bragg/product_master.csv
#bragg/source_master.csv"
#bragg/customer_master.csv"
#chs/product_master.csv"
