import os
import json
import logging
import pandas as pd
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import CSVLoader


from utils import utils

ENTITY_SHEET = "CONFIG_DATA_ENTITIES"
MAPPING_SHEET = "CONFIG_DATA_ENTITY_MAP"

class EntityDocumentProvider:
    def __init__(self, tenant_path: str, max_docs: int = 50):
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
            raise ValueError(f"{manifest_path} does not exist")
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
            tmp_file = f"/tmp/{self.tenant_path}_{entity_file_name}"
            try:
                data_df = pd.read_csv(master_data_file, nrows=self.max_docs)
                data_df.to_csv(tmp_file)
                master_loader = CSVLoader(tmp_file)
                docs = master_loader.load()
                for doc in docs:
                    doc.metadata.update(entity_config)
                entity_docs.extend(docs)
            finally:
                # remove the temp file
                tmp_path = Path(tmp_file)
                if tmp_path.exists():
                    os.remove(tmp_file)

        return entity_docs




