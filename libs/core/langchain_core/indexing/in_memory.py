import uuid
from typing import Any, Dict, List, Optional, Sequence, cast

from langchain_core.documents import Document
from langchain_core.indexing import UpsertResponse
from langchain_core.indexing.base import (
    AsyncDocumentIndexer,
    DeleteResponse,
    DocumentIndexer,
)


class InMemoryDocumentIndexer(DocumentIndexer):
    """In memory sync indexer."""

    def __init__(self, *, store: Optional[Dict[str, Document]] = None) -> None:
        """An in memory implementation of a document indexer."""
        self.store = store if store is not None else {}

    def upsert(self, items: Sequence[Document], /, **kwargs: Any) -> UpsertResponse:
        """Upsert items into the indexer."""
        ok_ids = []

        for item in items:
            if item.id is None:
                id_ = str(uuid.uuid4())
                item_ = item.copy()
                item_.id = id_
            else:
                item_ = item
                id_ = item.id

            self.store[id_] = item_
            ok_ids.append(cast(str, item_.id))

        return UpsertResponse(succeeded=ok_ids, failed=[])

    def delete(self, ids: Optional[List[str]] = None, **kwargs: Any) -> DeleteResponse:
        """Delete by ID."""
        if ids is None:
            raise ValueError("IDs must be provided for deletion")

        ok_ids = []

        for id_ in ids:
            if id_ in self.store:
                del self.store[id_]
                ok_ids.append(id_)

        return DeleteResponse(
            succeeded=ok_ids, num_deleted=len(ok_ids), num_failed=0, failed=[]
        )

    def get(self, ids: Sequence[str], /, **kwargs: Any) -> List[Document]:
        """Get by ids."""
        found_documents = []

        for id_ in ids:
            if id_ in self.store:
                found_documents.append(self.store[id_])

        return found_documents


class AsyncInMemoryDocumentIndexer(AsyncDocumentIndexer):
    """An in memory async indexer implementation."""

    def __init__(self, *, store: Optional[Dict[str, Document]] = None) -> None:
        """An in memory implementation of a document indexer."""
        self.indexer = InMemoryDocumentIndexer(store=store)

    async def upsert(
        self, items: Sequence[Document], /, **kwargs: Any
    ) -> UpsertResponse:
        """Upsert items into the indexer."""
        return self.indexer.upsert(items, **kwargs)

    async def delete(
        self, ids: Optional[List[str]] = None, **kwargs: Any
    ) -> DeleteResponse:
        """Delete by ID."""
        return self.indexer.delete(ids, **kwargs)

    async def get(self, ids: Sequence[str], /, **kwargs: Any) -> List[Document]:
        """Get by ids."""
        return self.indexer.get(ids, **kwargs)
