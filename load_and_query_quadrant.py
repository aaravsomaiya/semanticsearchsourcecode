import json

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import openai
import csv

client = QdrantClient(url= #add URL,
                      api_key= #add API Key)
openai.api_key = #API KEY

collection = "openai"
vector_size = 1536
embed_model = "text-embedding-ada-002"

client.recreate_collection(
    collection_name=collection,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
)

CSV_PATH = #add resources registry


def get_embedding(text: str) -> list[float]:
    resp = openai.embeddings.create(
        model=embed_model,
        input=text,
        encoding_format="float"
    )
    return resp.data[0].embedding


with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    i = 0
    for row in reader:
        text_to_embed = (row.get("title", "") + " " + row.get("description", "")).strip()
        if not text_to_embed:
            continue
        vector = get_embedding(text_to_embed)
        print(vector)
        point_id = int(row.get("id"))
        row = dict(row)
        payload = {"nav_url": row["nav_url"],
                   "title": row["title"],
                   "type": row["registry_type"],
                   "tags": row["tags"],
                   "company_id": row["company_id"],
                   "desc": row["description"],
                   "is_popular": row["is_popular"],
                   #"extra_nav_urls": [json.loads(i) for i in row["extra_nav_urls"]],
                  #"base_filters": json.loads(row["base_filters"])}"
                   }
        point = PointStruct(id=point_id, vector=vector, payload=dict(row))
        print(point)
        client.upsert(collection_name=collection, points=[point])
