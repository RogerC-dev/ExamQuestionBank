"""
RAG (Retrieval-Augmented Generation) Service
Provides vector database functionality for retrieving relevant legal content
to reduce AI token costs by 40-60%
"""
import os
import logging
from typing import List, Dict, Optional, Any
from django.conf import settings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for legal content retrieval"""

    def __init__(self):
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize()

    def _initialize(self):
        """Initialize ChromaDB client and embedding model"""
        try:
            # Initialize ChromaDB client
            chroma_path = os.path.join(settings.BASE_DIR, 'chroma_db')
            os.makedirs(chroma_path, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=chroma_path,
                settings=Settings(anonymized_telemetry=False)
            )

            # Get or create collection
            collection_name = "legal_knowledge_base"
            try:
                self.collection = self.client.get_collection(name=collection_name)
            except Exception:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "Legal knowledge base for Taiwan lawyer/judicial exams"}
                )

            # Initialize embedding model (using multilingual model for Chinese)
            try:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}. Using fallback.")
                # Fallback to a simpler model if the above fails
                try:
                    self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                except Exception as e2:
                    logger.error(f"Failed to load fallback embedding model: {e2}")

            logger.info("RAG service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self.client = None
            self.collection = None
            self.embedding_model = None

    def is_configured(self) -> bool:
        """Check if RAG service is properly configured"""
        return self.client is not None and self.collection is not None and self.embedding_model is not None

    def add_document(self, text: str, metadata: Dict[str, Any], doc_id: Optional[str] = None) -> bool:
        """
        Add a document to the vector database

        Args:
            text: Document text content
            metadata: Metadata dictionary (e.g., {'subject': '民法', 'type': 'law', 'year': 2023})
            doc_id: Optional document ID

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.warning("RAG service not configured, skipping document addition")
            return False

        try:
            # Generate embedding
            embedding = self.embedding_model.encode(text).tolist()

            # Prepare metadata
            metadata_str = {k: str(v) for k, v in metadata.items()}

            # Add to collection
            if doc_id:
                self.collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata_str],
                    ids=[doc_id]
                )
            else:
                self.collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata_str]
                )

            logger.info(f"Document added to RAG database: {metadata.get('subject', 'Unknown')}")
            return True

        except Exception as e:
            logger.error(f"Error adding document to RAG: {e}")
            return False

    def add_documents_batch(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add multiple documents in batch

        Args:
            documents: List of dicts with 'text', 'metadata', and optionally 'id'

        Returns:
            Number of successfully added documents
        """
        if not self.is_configured():
            return 0

        added_count = 0
        texts = []
        metadatas = []
        ids = []
        embeddings = []

        try:
            for doc in documents:
                text = doc.get('text', '')
                metadata = doc.get('metadata', {})
                doc_id = doc.get('id', None)

                if not text:
                    continue

                embedding = self.embedding_model.encode(text).tolist()
                metadata_str = {k: str(v) for k, v in metadata.items()}

                texts.append(text)
                metadatas.append(metadata_str)
                embeddings.append(embedding)
                if doc_id:
                    ids.append(doc_id)

            if texts:
                if ids and len(ids) == len(texts):
                    self.collection.add(
                        embeddings=embeddings,
                        documents=texts,
                        metadatas=metadatas,
                        ids=ids
                    )
                else:
                    self.collection.add(
                        embeddings=embeddings,
                        documents=texts,
                        metadatas=metadatas
                    )
                added_count = len(texts)

            logger.info(f"Added {added_count} documents to RAG database in batch")
            return added_count

        except Exception as e:
            logger.error(f"Error adding documents batch to RAG: {e}")
            return added_count

    def retrieve(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents based on query

        Args:
            query: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {'subject': '民法'})

        Returns:
            List of relevant documents with metadata
        """
        if not self.is_configured():
            logger.warning("RAG service not configured, returning empty results")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Prepare where clause for filtering
            where = None
            if filter_metadata:
                where = {k: str(v) for k, v in filter_metadata.items()}

            # Query collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )

            # Format results
            retrieved_docs = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    doc = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    }
                    retrieved_docs.append(doc)

            logger.debug(f"Retrieved {len(retrieved_docs)} documents for query: {query[:50]}")
            return retrieved_docs

        except Exception as e:
            logger.error(f"Error retrieving from RAG: {e}")
            return []

    def get_context_for_essay_grading(self, subject: str, question_text: str, answer_text: str) -> str:
        """
        Get relevant context for essay grading

        Args:
            subject: Subject name (e.g., '民法')
            question_text: Essay question text
            answer_text: Student's answer text

        Returns:
            Formatted context string for AI
        """
        # Retrieve relevant legal content
        query = f"{subject} {question_text}"
        relevant_docs = self.retrieve(query, n_results=3, filter_metadata={'subject': subject})

        if not relevant_docs:
            # Fallback: retrieve without subject filter
            relevant_docs = self.retrieve(query, n_results=3)

        # Format context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"相關法條/判例：{doc['text'][:500]}")

        context = "\n\n".join(context_parts)
        return context

    def get_context_for_question_generation(self, subject: str, topic: Optional[str] = None) -> str:
        """
        Get relevant context for question generation

        Args:
            subject: Subject name
            topic: Optional specific topic

        Returns:
            Formatted context string
        """
        query = f"{subject}"
        if topic:
            query += f" {topic}"

        relevant_docs = self.retrieve(query, n_results=5, filter_metadata={'subject': subject})

        if not relevant_docs:
            relevant_docs = self.retrieve(query, n_results=5)

        context_parts = []
        for doc in relevant_docs:
            context_parts.append(doc['text'][:300])

        context = "\n\n".join(context_parts)
        return context

    def delete_collection(self):
        """Delete the entire collection (use with caution)"""
        if self.client and self.collection:
            try:
                self.client.delete_collection(name=self.collection.name)
                self.collection = None
                logger.warning("RAG collection deleted")
            except Exception as e:
                logger.error(f"Error deleting collection: {e}")


# Create singleton instance
rag_service = RAGService()



