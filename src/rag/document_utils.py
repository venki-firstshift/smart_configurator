from langchain_core.documents import Document
import csv
import uuid
GLOBAL_CONFIG_MAP = dict()

ENTITY_KEYS = [
    'ENTITY_CATEGORY', 'ENTITY_NAME', 'ENTITY_SOURCE', 'ENTITY_TYPE', 'DIMENSION_SEQUENCE',
    'DIMENSION_TYPE', 'DD1_PK', 'DD2_PK','DD3_PK', 'DD4_PK', 'DD5_PK'
]

ENTITY_TEMPLATE = """
    irrespective of the order, if a given list of columns approximately match {columns}, then config is: "{config_key}"
"""
ENTITY_QUERY_TEMPLATE = """
    Given columns {columns} return config 
"""
def headers_to_text(headers: [str], meta_data: dict) -> str:
    # convert headers into a doc
    if 'UU_ID' in headers: headers.remove('UU_ID')
    columns = ",".join([ f"\"{hd}\"" for hd in headers])

    #entity_config = {ek:meta_data[ek] for ek in ENTITY_KEYS}
    entity_config = {f"|{ek}:{meta_data[ek]}|" for ek in ENTITY_KEYS}
    entity_config_str = " ".join(entity_config)
    # config_id = str(uuid.uuid4())
    # GLOBAL_CONFIG_MAP[config_id] = entity_config
    text_doc = ENTITY_TEMPLATE.format(columns=columns, config_key=entity_config_str)
    return text_doc

def make_document(headers: [str], meta_data: dict) -> Document:
    doc_text = headers_to_text(headers, meta_data)
    header_doc = Document(doc_text, metadata=meta_data)
    return header_doc

def prepare_entity_question(test_file) -> str:
    with open(test_file, 'r') as f:
        dict_reader = csv.DictReader(f)
        headers = list(dict_reader.fieldnames)
    if 'UU_ID' in headers: headers.remove('UU_ID')
    cols = ",".join([f"\"{hd}\"" for hd in headers])
    query_doc = ENTITY_QUERY_TEMPLATE.format(columns=cols)
    return query_doc