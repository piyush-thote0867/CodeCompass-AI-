# CodeCompass AI

Paste a GitHub repo URL, get a plain-language overview, a dependency graph, and answers to questions about it — using hybrid retrieval (FAISS + import graph), not just plain RAG.

**Live demo:** 
**Repo:** [https://codecampass-ai.streamlit.app/]
repos to use : https://github.com/pallets/flask

---

## Need
Plain RAG misses structurally related files that don't share vocabulary with your question. CodeCompass combines semantic search (FAISS) with an actual import-dependency graph (NetworkX) so retrieval includes files that are *connected*, not just *similar*.

## Usage
1. Paste a GitHub URL → click **Analyze repo**.
2. Get an auto-generated overview + dependency graph.
3. Ask a specific question — answer is grounded in retrieved code (semantic + structural).

## Technology Used
- **Parsing:** Python `ast`
- **Graph:** NetworkX
- **Vector search:** FAISS + sentence-transformers (`all-MiniLM-L6-v2`)
- **Answers:** Groq (LLaMA 3.3-70B-versatile)
- **Document fallback:** pypdf
- **Visualization:** matplotlib
- **Frontend:** Streamlit (with session-state caching)
- **Deployment:** Streamlit Community Cloud

## Constraints
- Python-only parsing (uses Python's `ast`) — detects and explains non-Python or document-only repos instead of failing silently.
- LLM answers are prompt-constrained to context, not guaranteed grounded.
- Free-tier compute — large repos (Django) run slower.

## Version
**Version 1** — made by Piyush.

## Upcoming Work
- Multi-language parsing (tree-sitter)
- Return graph directly instead of rebuilding for visualization
- Show retrieved context in UI by default
