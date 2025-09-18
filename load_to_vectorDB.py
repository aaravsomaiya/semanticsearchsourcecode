"""
Read registry and populate qdrant
"""
import asyncio
import csv
import json
import logging

from openai import AsyncOpenAI
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import TextIndexType, PointStruct

from load_and_query_quadrant import collection

openai = AsyncOpenAI(api_key=#AddAPIKEY)

collection_name = "spotlight_main"
items = []
points = []


MODEL = "text-embedding-3-large"
# MODEL = "text-embedding-ada-002"
MODEL_DIMS = 3072
# MODEL_DIMS = 1536

CSV_PATH = "sample_pebble_resources_registry.csv"

async def get_items_from_registry():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        i=0
        for row in reader:
            text_to_embed = (row.get("title", "") + " " + row.get("description", "")).strip()
            if not text_to_embed:
                continue
            vector = await get_embedding(row)
            print(vector)
            point_id = int(row.get("id"))

            point = PointStruct(id=point_id, vector=vector, payload=dict(row))
            points.append(point)
            i+=1
            if i>10 : break

async def get_embedding(row):
    # print(row)
    # print("desc ", row["description"])

    desc = row["description"]
    if not desc:
        desc = f"{row["title"]} is a KPI"

    res = (
        await openai.embeddings.create(
            model=MODEL, input=desc
        )
    ).data[0]
    res = res.embedding

    points.append(
        models.PointStruct(
            id=row["id"],
            payload={
                "nav_url": row["nav_url"],
                "title": row["title"],
                "type": row["registry_type"],
                "tags": row["tags"],
                "company_id": row["company_id"],
                "desc": row["description"],
                "is_popular": row["is_popular"],
                "extra_nav_urls": [json.loads(i) for i in row["extra_nav_urls"]],
                "base_filters": json.loads(row["base_filters"])
            },
            vector=res,
        )
    )


async def populate_embeddings():
    await asyncio.gather(*[get_embedding(row) for row in items])


# try:
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# except:
# loop = asyncio.get_event_loop()

loop.run_until_complete(get_items_from_registry())
print("Got Items: ", len(items), items[0])
loop.run_until_complete(populate_embeddings())

qdrant_client = QdrantClient(url=#ADDURL,
                      api_key=#ADDAPIKEY)

qdrant_client.recreate_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=MODEL_DIMS, distance=models.Distance.COSINE,
    ),
    optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000),
    quantization_config=models.ScalarQuantization(
        scalar=models.ScalarQuantizationConfig(
            type=models.ScalarType.INT8,
            always_ram=True,
        ),
    ),
)
qdrant_client.create_payload_index(
    collection_name=collection_name,
    field_name="company_id",
    field_schema="keyword"
)
qdrant_client.create_payload_index(
    collection_name=collection_name,
    field_name="title",
    field_schema=models.TextIndexParams(
        type=TextIndexType.TEXT,
        tokenizer=models.TokenizerType.PREFIX,
        min_token_len=2,
        max_token_len=15,
        lowercase=True,
    ),
)
print("Total number of points: ", len(points))
for i in range(0, len(points), 200):
    print(f"Upserting points {i} to {i+200}")
    qdrant_client.upsert(collection_name="spotlight_main", points=points[i:i+200] )

print("Done")
