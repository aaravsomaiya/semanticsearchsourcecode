This repo shows a full mini-pipeline for:
- generating OpenAI embeddings from a CSV registry,
- writing them to Qdrant with useful payload indexes, and
- querying them with both plain semantic search and a “classified + filtered” search flow.

Prerequisites: 
As listed below
Python 3.10+
pip install qdrant-client openai
Environment variables:
OPENAI_API_KEY
QDRANT_URL
QDRANT_API_KEY

Model note: text-embedding-ada-002 (1536-D) is legacy. Prefer text-embedding-3-large (3072-D) or text-embedding-3-small (1536-D). Update your vector_size to match.
