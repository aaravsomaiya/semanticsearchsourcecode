import json
import time

from qdrant_client import QdrantClient
from qdrant_client.http import models

import openai

qdrant_client = QdrantClient(url= #addURL,
                             api_key= #addAPIKey)

openai.api_key = #addAPIKEY

COLLECTION_NAME = "spotlight_main"

embed_model = "text-embedding-3-large"

LLM_MODEL = "gpt-4.1-nano"

PROMPT = #Add Classifier Guidlines or Prompt



def get_embedding(text: str) -> list[float]:
    resp = openai.embeddings.create(
        model=embed_model,
        input=text,
        encoding_format="float"
    )
    return resp.data[0].embedding


def get_classification_and_filters(q: str):
    """
    :param q: input query
    :return: Structured response, for example:
        {
          "categories": [
            { "name": "budgets", "weight": 0.5 },
            { "name": "kpi", "weight": 0.3 },
            { "name": "reports", "weight": 0.2 }
          ],
          "filters": {
            "start_date": null,
            "end_date": null,
            "program_name": null,
            "aggregation": "yearly"
          }
    }
    """

    response = openai.responses.create(
        model=LLM_MODEL,
        instructions=PROMPT,
        input=q
    )
    output = response.output_text
    classification_response = {}
    # Extract only the JSON content between { and }
    json_start = output.find('{')
    json_end = output.rfind('}') + 1
    if json_start != -1 and json_end != -1:
        classification_response = json.loads(output[json_start:json_end])

    return classification_response


def search(
        q: str,
):
    query_vector = get_embedding(q)

    classification_response = get_classification_and_filters(q)
    print("Classification response: ", classification_response)

    sorted_matching_types = sorted(
        classification_response["categories"],
        key=lambda x: x["weight"],
        reverse=True
    )

    semantic_res = []
    for registry_type in sorted_matching_types:
        vector_res = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="type", match=models.MatchValue(value=str(registry_type["name"]))
                    )
                ]
            ),
            query=query_vector,
            with_vectors=False,
            limit=int(10 * (registry_type["weight"] or 0.1)),
            with_payload=True,
        )
        semantic_res.extend(vector_res.points)
    # Ignore irrelevant results.
    # semantic_res = []
    # for result in vector_res:
    #     new_score = round(result.score * 100)
    #     if new_score <= 20:
    #         break
    #     semantic_res.append(result)
    return semantic_res


qdrant_client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="type",
    field_schema="keyword"
)

inp = input("Enter query: ")
print("Processing...")
start_time = time.time()
res = search(inp)
end_time = time.time()
print(f"Search completed in {end_time - start_time:.2f} seconds")
print("Results: ")
for r in res:
    print(r.payload["title"], r.score, r.payload["type"])