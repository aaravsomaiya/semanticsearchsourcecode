This repository provides a reusable Python pipeline for building semantic search systems. It shows how to embed any text data set (not just the sample CSV) with OpenAI models, store the vectors in a Qdrant database, and query them using natural language. You can drop in your own data—product catalogs, research papers, support tickets, internal documents—and immediately gain fast, scalable semantic search capabilities with minimal code changes.


Prerequisites: 
As listed below
Python 3.10+
pip install qdrant-client openai
Environment variables:
OPENAI_API_KEY
QDRANT_URL
QDRANT_API_KEY

Model note: text-embedding-ada-002 (1536-D) is legacy. Prefer text-embedding-3-large (3072-D) or text-embedding-3-small (1536-D). Update your vector_size to match.
