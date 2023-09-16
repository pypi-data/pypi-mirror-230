"""**Docstores** are classes to store and load Documents.

The **Docstore** is a simplified version of the Document Loader.

**Class hierarchy:**

.. code-block::

    Docstore --> <name> # Examples: InMemoryDocstore, Wikipedia

**Main helpers:**

.. code-block::

    Document, AddableMixin
"""
from langchainmulti.docstore.arbitrary_fn import DocstoreFn
from langchainmulti.docstore.in_memory import InMemoryDocstore
from langchainmulti.docstore.wikipedia import Wikipedia

__all__ = ["DocstoreFn", "InMemoryDocstore", "Wikipedia"]
