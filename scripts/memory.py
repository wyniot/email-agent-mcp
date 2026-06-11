"""memory.py - Email memory module for the Email Agent.

In-memory storage by default (always works).
Chroma vector store is used when langchain is available (optional enhancement).
"""

from typing import Any
from config import Config


class EmailMemory:
    """Lightweight memory wrapper.

    Default: in-memory list (always works, no dependencies).
    Enhanced: Chroma vector store when langchain is installed.
    """

    def __init__(self):
        self._store: list[dict[str, Any]] = []
        self._use_vector = False

        # Try Chroma vector store (optional, needs langchain installed)
        if not Config.MOCK_MODE:
            try:
                self._init_chroma()
            except Exception:
                pass  # Silently fall back to in-memory

    def _init_chroma(self):
        """Try to initialize Chroma. Silently skip if deps missing."""
        try:
            from langchain.vectorstores import Chroma as _Chroma
            from langchain.embeddings.openai import OpenAIEmbeddings as _Emb
            from langchain.memory import VectorStoreRetrieverMemory as _Mem

            embeddings = _Emb(openai_api_key=Config.OPENAI_API_KEY)
            vs = _Chroma(
                collection_name="email_memory",
                embedding_function=embeddings,
                persist_directory=Config.CHROMA_PERSIST_DIR,
            )
            self._retriever = _Mem(
                retriever=vs.as_retriever(search_kwargs={"k": 3}),
                memory_key="chat_history",
                return_messages=True,
            )
            self._use_vector = True
            self._vector_store = vs
        except ImportError:
            pass  # langchain / chroma not installed - in-memory fallback is fine
        except Exception:
            pass  # Any other setup issue - use in-memory

    def save_interaction(self, email_id, subject, analysis, reply):
        record = {"email_id": email_id, "subject": subject,
                  "analysis": analysis, "reply": reply}
        self._store.append(record)
        if self._use_vector:
            try:
                self._retriever.save_context(
                    {"input": "处理邮件: %s" % subject},
                    {"output": "分析: %s\n回复: %s" % (analysis, reply)},
                )
            except Exception:
                pass

    def get_history(self, limit=5):
        return self._store[-limit:]

    def query_similar(self, query, k=3):
        if self._use_vector:
            try:
                docs = self._retriever.load_memory_variables({"input": query})
                return [str(h) for h in docs.get("chat_history", [])]
            except Exception:
                pass
        return []
