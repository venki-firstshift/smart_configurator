import os
import json
import logging
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import CSVLoader
import csv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from rag.document_utils import make_document

from utils import utils

ENTITY_SHEET = "CONFIG_DATA_ENTITIES"
MAPPING_SHEET = "CONFIG_DATA_ENTITY_MAP"

class EntityDocumentProvider:
    def __init__(self, tenant_path: str, max_docs: int = 100):
        self.tenant_path = tenant_path
        self.max_docs = max_docs

    @classmethod
    def _get_meta_data(cls,entities, entity_name):
        entity_rows = entities.loc[entities['ENTITY_NAME'] == entity_name]
        entity_rows = entity_rows.head(1)
        entity_rows.fillna(0, inplace=True)
        entity_meta_values= entity_rows.to_dict('records')
        entity_meta = entity_meta_values[0]
        return entity_meta

    def get_documents(self) -> [Document]:
        data_root_dir = utils.read_env_variable("TENANT_DATA_DIR", "./test_data/Tenant_Config_Samples")
        manifest_path = f"{data_root_dir}/{self.tenant_path}/manifest.json"
        path = Path(manifest_path)
        if not path.exists():
            raise ValueError(f"{manifest_path} does not exist")

        with open(manifest_path) as fp:
            manifest = json.load(fp)

        config_name = manifest.get("config", None)
        if config_name is None:
            raise ValueError(f"{manifest_path} does not specify configuration XLSX file")
        config_file = f"{data_root_dir}/{self.tenant_path}/{config_name}"
        path = Path(config_file)
        if not path.exists():
            raise ValueError(f"{config_file} does not exist")
        # read CONFIG_DATA_ENTITIES
        entities = pd.read_excel(config_file, sheet_name=ENTITY_SHEET)
        # read CONFIG_DATA_ENTITY_MAP

        data_files = manifest.get("files", None)
        if data_files is None or len(data_files) == 0:
            logging.warning(f"There are not files specified to process in {manifest_path}")
            return []
        entity_docs = []
        for entity_details in data_files:
            entity_name = entity_details[0]
            entity_file_name = entity_details[1]
            logging.debug(f"Processing  documents for entity {entity_name} from file {entity_file_name}")
            entity_config = self._get_meta_data(entities, entity_name)
            master_data_file = f"{data_root_dir}/{self.tenant_path}/{entity_file_name}"
            # use CSV loader to get documents
            # first truncate to max rows
            # tmp_file = f"/tmp/{self.tenant_path}_{entity_file_name}"
            # try:
            #     data_df = pd.read_csv(master_data_file, nrows=self.max_docs)
            #     data_df.to_csv(tmp_file)
            #     master_loader = CSVLoader(tmp_file)
            #     docs = master_loader.load()
            #     for doc in docs:
            #         doc.metadata.update(entity_config)
            #     entity_docs.extend(docs)
            # finally:
            #     # remove the temp file
            #     tmp_path = Path(tmp_file)
            #     if tmp_path.exists():
            #         os.remove(tmp_file)

            with open(master_data_file, 'r') as f:
                dict_reader = csv.DictReader(f)
                headers = list(dict_reader.fieldnames)
            # convert headers into a doc
            header_doc = make_document(headers, meta_data=entity_config)
            entity_docs.append(header_doc)

        return entity_docs




class DocumentStoreBuilder:
    def __init__(self, search_type: str="similarity_score_threshold", search_kwargs: dict=None):
        self.search_type = search_type
        self.search_kwargs = search_kwargs if search_kwargs is not None else dict(k=6, score_threshold=0.5)
        self.docs = []
        self.vectorstore = None
        self.retriever = None

    def add_tenant_entity_data(self, tenant_path: str, max_docs: int = 100):
        tenant_docs_provider = EntityDocumentProvider(tenant_path, max_docs)
        tenant_docs = tenant_docs_provider.get_documents()
        self.docs.extend(tenant_docs)

    def build_store_as_retriever(self):
        if len(self.docs) == 0:
            raise ValueError("There are not documents processed and nothing to build a document store")
        self.vectorstore = Chroma.from_documents(documents=self.docs, embedding=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever(search_type=self.search_type, search_kwargs=self.search_kwargs)
        return self.retriever

