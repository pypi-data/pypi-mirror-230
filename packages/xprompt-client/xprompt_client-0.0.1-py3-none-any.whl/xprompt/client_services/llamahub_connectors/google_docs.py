"""
Create google oauth credentials
https://developers.google.com/docs/api/quickstart/python

1. Enable API
2. Create OAuth 2.0 Client using web application
3. download and rename to credentials.json, and then place is next to where you run xprompt
"""

from xprompt_common.base_service import BaseService
from llama_index import download_loader


class GoogleDoc(BaseService):
    doc_id: str = ""

    def run(self) -> str:
        google_docs_reader = download_loader("GoogleDocsReader")

        gdoc_ids = [self.doc_id]
        loader = google_docs_reader()
        documents = loader.load_data(document_ids=gdoc_ids)
        if len(documents) == 0:
            return ""

        return documents[0].text
