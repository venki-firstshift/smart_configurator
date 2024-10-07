import logging

from langchain_core.prompts import PromptTemplate
from sympy.physics.units import temperature

logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.ERROR)
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain import hub
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI

from rag.document_store import DocumentStoreBuilder
from rag.document_utils import prepare_entity_question

from utils import utils
from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field


class EntityConfig(BaseModel):
    columns: List[str] = Field(default_factory=list)
    config: str = Field(description="UUID of Configuration")

model = ChatOpenAI(temperature=0)
# , model_kwargs={'response_format': {'type': 'json_object'}}
# model = llm_model.with_structured_output(EntityConfig, method="json_mode")

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


def format_question(file_path):
    data_dir = utils.read_env_variable("TENANT_DATA_DIR", "./test_data/Tenant_Config_Samples")
    if file_path == 'quit':
        exit(0)
    master_file = f"{data_dir}/{file_path}"
    doc_content = prepare_entity_question(master_file)
    return doc_content

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def create_qa_chain():
    question_reader = RunnableLambda(format_question)
    entity_retriever = prepare_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    #llm_model = model.with_structured_output(method="json_mode")
    qa_chain = (
            {"context" : entity_retriever, "question": question_reader}
            | prompt
            | model
            | StrOutputParser()
    )
    return qa_chain


def discover_entities(llm_chain):
    while True:
        file_path = input('Enter path to master data file (quit to end) : ')
        file_path = file_path.strip()
        if file_path == 'quit':
            exit(0)
        result = llm_chain.invoke(file_path)
        print(result)

if __name__ == '__main__':
    print("Running a Q&A Loop")
    rag_chain = create_qa_chain()
    #rag_chain = create_qa_chain_with_sources()
    discover_entities(rag_chain)


def create_qa_chain_with_sources():
    entity_retriever = prepare_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
            | prompt
            | model
            | StrOutputParser()
    )
    question_reader = RunnableLambda(format_question)
    rag_chain_with_source = RunnableParallel(
        {"context": entity_retriever, "question": question_reader}
    ).assign(answer=rag_chain_from_docs)
    return rag_chain_with_source
