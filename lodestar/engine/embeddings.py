"""
ChromaDB vector database interface for Lodestar.

Manages persistent embeddings for policy documents, enabling semantic
similarity search across the global policy knowledge base.
"""

import logging
import os
from typing import Any

import chromadb

logger = logging.getLogger(__name__)

COLLECTION_NAME = "lodestar_policies"


class EmbeddingsDB:
    """
    ChromaDB-backed vector store for policy embeddings.

    Persists to disk at CHROMA_PERSIST_DIR for reuse across sessions.
    Uses ChromaDB's built-in embedding function by default.
    """

    def __init__(self, persist_dir: str | None = None) -> None:
        """
        Initialize the embeddings database.

        Args:
            persist_dir: Directory for ChromaDB persistence.
                         Defaults to CHROMA_PERSIST_DIR env var or './.chroma'.
        """
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./.chroma")
        self.client: chromadb.ClientAPI | None = None
        self.collection: chromadb.Collection | None = None
        logger.debug("EmbeddingsDB configured with persist_dir=%s", self.persist_dir)

    def initialize_db(self) -> None:
        """
        Initialize or connect to the ChromaDB instance.

        Creates the persistence directory if needed and gets or creates
        the policies collection.
        """
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        count = self.collection.count()
        logger.info("ChromaDB initialized: %d policies in collection", count)

    def _ensure_initialized(self) -> None:
        """Raise RuntimeError if the DB has not been initialized."""
        if self.collection is None:
            raise RuntimeError(
                "EmbeddingsDB not initialized. Call initialize_db() first."
            )

    def add_policy(self, policy: dict[str, Any]) -> None:
        """
        Add a policy document to the vector store.

        The policy dict is expected to have at minimum: id, name, description,
        domain, country. The document text combines key fields for embedding.

        Args:
            policy: Policy dict (from seed_policies.json or Pydantic model).

        Raises:
            RuntimeError: If DB is not initialized.
            KeyError: If required policy fields are missing.
        """
        self._ensure_initialized()
        policy_id = policy["id"]
        doc_text = (
            f"Policy: {policy['name']}\n"
            f"Country: {policy['country']}\n"
            f"Domain: {policy['domain']}\n"
            f"Description: {policy['description']}\n"
            f"Key outcomes: {'; '.join(policy.get('key_outcomes', []))}\n"
            f"Success factors: {'; '.join(policy.get('success_factors', []))}"
        )
        metadata = {
            "name": policy["name"],
            "country": policy["country"],
            "city": policy.get("city", ""),
            "domain": policy["domain"],
            "year_start": str(policy.get("year_start", "")),
        }
        existing = self.collection.get(ids=[policy_id])
        if existing["ids"]:
            logger.debug("Policy %s already exists, updating", policy_id)
            self.collection.update(
                ids=[policy_id],
                documents=[doc_text],
                metadatas=[metadata],
            )
        else:
            self.collection.add(
                ids=[policy_id],
                documents=[doc_text],
                metadatas=[metadata],
            )
            logger.info("Added policy: %s (%s)", policy["name"], policy_id)

    def search_similar(self, query: str, n_results: int = 3) -> list[dict[str, Any]]:
        """
        Search for policies semantically similar to a query.

        Args:
            query: Natural language query describing the target context.
            n_results: Number of top results to return.

        Returns:
            List of dicts, each with keys: id, document, metadata, distance, similarity_score.

        Raises:
            RuntimeError: If DB is not initialized.
        """
        self._ensure_initialized()
        if self.collection.count() == 0:
            logger.warning("Policy collection is empty. Run 'lodestar ingest' first.")
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count()),
        )
        output = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        for i, policy_id in enumerate(ids):
            similarity = 1.0 - distances[i]
            output.append(
                {
                    "id": policy_id,
                    "document": documents[i],
                    "metadata": metadatas[i],
                    "distance": distances[i],
                    "similarity_score": round(similarity, 4),
                }
            )
        logger.debug("Found %d similar policies for query", len(output))
        return output

    def get_all_policies(self) -> list[dict[str, Any]]:
        """
        Retrieve all policy documents from the collection.

        Returns:
            List of dicts with keys: id, document, metadata.

        Raises:
            RuntimeError: If DB is not initialized.
        """
        self._ensure_initialized()
        if self.collection.count() == 0:
            return []
        results = self.collection.get()
        output = []
        for i, policy_id in enumerate(results["ids"]):
            output.append(
                {
                    "id": policy_id,
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i],
                }
            )
        return output
