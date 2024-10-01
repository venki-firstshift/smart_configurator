import json

from utils import utils

from rag.document_store import DocumentStoreBuilder
from rag.document_utils import prepare_entity_question
import csv
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.ERROR)

# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

model = ChatOpenAI(temperature=0)

ENTITY_KEYS = [
    'ENTITY_CATEGORY', 'ENTITY_NAME', 'ENTITY_SOURCE', 'ENTITY_TYPE', 'DIMENSION_SEQUENCE',
    'DIMENSION_TYPE', 'DD1_PK', 'DD2_PK','DD3_PK', 'DD4_PK', 'DD5_PK'
]
def prepare_retriever():
    store_builder = DocumentStoreBuilder()
    # add documents to the builder before building
    tenant_data_paths = ['Std_Data', 'LLF_Data', 'Adient', 'VictoriaSecret']
    for tenant_data_path in tenant_data_paths:
        logging.info(f"Loading data from {tenant_data_path}")
        store_builder.add_tenant_entity_data(tenant_data_path)
    retriever = store_builder.build_store_as_retriever()
    return retriever

def create_qa_chain(doc_retriever):
    qa_chain = RetrievalQA.from_chain_type(model, retriever=doc_retriever)
    return qa_chain

def discover_entities(retriever):
    llm_chain = create_qa_chain(retriever)
    data_dir = utils.read_env_variable("TENANT_DATA_DIR", "./test_data/Tenant_Config_Samples")
    while True:
        file_path = input('Give the input file to discover entity(quit to end) : ')
        if file_path == 'quit':
            exit(0)
        master_file = f"{data_dir}/{file_path}"
        doc_content = prepare_entity_question(master_file)
        result = llm_chain.invoke({"query": doc_content})
        print(result["result"])
        # if matches is not None and len(matches) > 0:
        #     print(f"Matches : {len(matches)}")
        #     entity_config = {ek: matches[0].metadata[ek] for ek in ENTITY_KEYS}
        #     print(json.dumps(entity_config, indent=2))
        # else:
        #     print("There are no matches")

# def format_docs(docs):
#     if docs is None or len(docs) == 0:
#         return "There are no matching examples to guess the entity type"
#     else:
#         entity_doc = docs[0]
#         # return only some meta data fields
#         meta_data = entity_doc.metadata
#         entity_config = {  ek : meta_data.get(ek, None) for ek in ENTITY_KEYS }
#         return json.dumps(entity_config, indent=2)
#
# RAG_TEMPLATE = """
# You are an assistant for Configuration Building. Use the given samples to help me identify the entities from data files.
#
# <context>
# {context}
# </context>
#
# Give path to data CSV:
#
# {question}"""
#
# rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
# entity_retriever = prepare_retriever()
#
# bot_chain = (
#     RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
#     | rag_prompt
#     | model
#     | StrOutputParser()
# )
# rag_chain_with_source = RunnableParallel(
#     {"context": entity_retriever, "question": RunnablePassthrough()}
# ).assign(answer=bot_chain)
# headers = "Product ID,Product desc,Product type,Product line,Price ($),Cost ($),Shelf life"
# question = ",".join(sorted(headers.split(",")))
# result = rag_chain_with_source.invoke(question)
# print(result['context'][0].metadata)

if __name__ == '__main__':
    print("Running a Q&A Loop")
    entity_retriever = prepare_retriever()
    discover_entities(entity_retriever)