from langchain_core.documents import Document
import csv

ENTITY_TEMPLATE = """
    irrespective of the order, if a given list of columns approximately match {columns}, then entity is {entity_name} and its type is {entity_type}
"""
ENTITY_QUERY_TEMPLATE = """
    Given columns {columns} what is the entity and what is its type?
"""
def headers_to_text(headers: [str], meta_data: dict) -> str:
    # convert headers into a doc
    if 'UU_ID' in headers: headers.remove('UU_ID')
    columns = ",".join([ f"\"{hd}\"" for hd in headers])
    entity_name = meta_data["ENTITY_NAME"]
    entity_type = meta_data["ENTITY_TYPE"]
    text_doc = ENTITY_TEMPLATE.format(columns=columns, entity_name=entity_name, entity_type=entity_type)
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