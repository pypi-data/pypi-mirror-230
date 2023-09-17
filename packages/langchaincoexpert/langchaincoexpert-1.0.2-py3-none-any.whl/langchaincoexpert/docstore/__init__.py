"""**Docstores** are classes to store and load Documents.

The **Docstore** is a simplified version of the Document Loader.

**Class hierarchy:**

.. code-block::

    Docstore --> <name> # Examples: InMemoryDocstore, Wikipedia

**Main helpers:**

.. code-block::

    Document, AddableMixin
"""
from langchaincoexpert.docstore.arbitrary_fn import DocstoreFn
from langchaincoexpert.docstore.in_memory import InMemoryDocstore
from langchaincoexpert.docstore.wikipedia import Wikipedia

__all__ = ["DocstoreFn", "InMemoryDocstore", "Wikipedia"]
