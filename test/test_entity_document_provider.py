import logging
logging.basicConfig(level=logging.DEBUG)

from rag.document_store import EntityDocumentProvider

if __name__ == '__main__':
    document_provider = EntityDocumentProvider('VictoriaSecret', max_docs=100)
    docs = document_provider.get_documents()
    print(f"Total Docs : {len(docs)}")
    print(docs[0].page_content)
    print(docs[0].metadata)