from typing import List

from langchainmulti.callbacks.manager import CallbackManagerForRetrieverRun
from langchainmulti.schema import BaseRetriever, Document
from langchainmulti.utilities.wikipedia import WikipediaAPIWrapper


class WikipediaRetriever(BaseRetriever, WikipediaAPIWrapper):
    """`Wikipedia API` retriever.

    It wraps load() to get_relevant_documents().
    It uses all WikipediaAPIWrapper arguments without any change.
    """

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        return self.load(query=query)
