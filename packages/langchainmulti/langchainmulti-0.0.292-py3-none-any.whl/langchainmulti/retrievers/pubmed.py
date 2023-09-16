from typing import List

from langchainmulti.callbacks.manager import CallbackManagerForRetrieverRun
from langchainmulti.schema import BaseRetriever, Document
from langchainmulti.utilities.pubmed import PubMedAPIWrapper


class PubMedRetriever(BaseRetriever, PubMedAPIWrapper):
    """`PubMed API` retriever.

    It wraps load() to get_relevant_documents().
    It uses all PubMedAPIWrapper arguments without any change.
    """

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        return self.load_docs(query=query)
