from langchain_core import embeddings

from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import prompts

from logger import Logger
from database import ElasticsearchDatabase
import prompts
import config as cfg
from llm_model import LLMModel

_CHUNK_SIZE = 512
_CHUNK_OVERLAP = 20


class RAGManager:
    """
    RAGManager is a class that manages the documents to provide context for the model
    Use Elasticsearch to provide a vector store for the embedded documents
    """
    def __init__(self,
                 vector_store,
                 embeddings,
                 model : LLMModel ,
                 multi_threading : bool = False
        ):
        self._model = model
        self._embeddings = embeddings
        self._vector_store = vector_store

        self._multi_threading = multi_threading
        self._is_loaded = False
        self._logger = Logger()


    def retrieve(self, prompt : str) -> str:
        if not self._is_loaded:
            self._logger.error("RAG: No documents loaded")
            return ""

        retrieved_docs = self._vector_store.similarity_search(prompt)

        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        contextual_prompt = prompts.RAG_PROMPT(question=prompt, context=docs_content)

        return contextual_prompt

    def _load_from_directory(self, directory : str):
        loader = DirectoryLoader(
                path=directory,
                glob="**/*.md",
                load_hidden = False,
                recursive = True,
                use_multithreading = self._multi_threading,
                show_progress = True,
        )

        try:
            print(f"RAG: Loading documents from {directory}")
            rag_docs = loader.load()
            self._logger.info(f"RAG: Loaded {len(rag_docs)} documents from {directory}")
        except Exception as e:
            self._logger.error(f"Error loading documents from {directory}: {e}")
            exit(1)

        # set up text splitter
        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=_CHUNK_SIZE,
                chunk_overlap=_CHUNK_OVERLAP,
                length_function=self._model.token_count,
        )
        # splits
        splits = text_splitter.split_documents(rag_docs)

        ids = [f"{split.metadata['source']}_chunk_{i}" for i, split in enumerate(splits)]

        # index and store to vector store
        try:
            _ = self._vector_store.add_documents(documents=splits, ids=ids)
            self._logger.info(f"RAG: Added {len(rag_docs)} documents to vector store")
            self._is_loaded = True
        except Exception as e:
            self._logger.error(f"Error adding documents to vector store: {e}")
            exit(1)

    def update_rag_from_directory(self, directory : str, db : ElasticsearchDatabase):
        """
        should provided a directory of markdown files
        """
        self._is_loaded = False

        if db.instance.indices.exists(index=cfg.INDEX_VECTOR_STORE):
            db.instance.indices.delete(index=cfg.INDEX_VECTOR_STORE)

            self._logger.info(f"RAG: Deleted existing index {cfg.INDEX_VECTOR_STORE}")
        else:
            self._logger.info(f"RAG: No existing index {cfg.INDEX_VECTOR_STORE}")

        self._load_from_directory(directory)


def main():
    from llm_model import GeminiModel
    from database import ElasticsearchDatabase

    model = GeminiModel()
    es_db = ElasticsearchDatabase()

    embeddings = model.embedding
    vector_store = es_db.set_vector_store(embeddings=embeddings)

    rag_manager = RAGManager(vector_store, embeddings, model)
    # rag_manager.load_from_directory("../rag")
    rag_manager.update_rag_from_directory("../rag", es_db)


if __name__ == "__main__":
    main()
