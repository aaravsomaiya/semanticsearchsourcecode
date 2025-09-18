from qdrant_client import QdrantClient
import openai
from qdrant_client.http.models import Distance, VectorParams, PointStruct, MatchValue, Filter, FieldCondition

client = QdrantClient(url=#addURL,
                      api_key=#addAPIKEY)
openai.api_key = #addAPIKEY

# embedding_1 = openai.embeddings.create(
#     model="text-embedding-ada-002",
#     input="This person is tall",
#     encoding_format="float"
# )
#
# embedding_2 = openai.embeddings.create(
#     model="text-embedding-ada-002",
#     input="This person is short",
#     encoding_format="float"
# )
#
# embedding_3 = openai.embeddings.create(
#     model="text-embedding-ada-002",
#     input="This person is fat",
#     encoding_format="float"
# )
# # client.recreate_collection(collection_name="openai", vectors_config=VectorParams(size=1536, distance=Distance.COSINE))
#
# client.upsert("openai", points=[
#     PointStruct(id=1, vector=embedding_1.data[0].embedding, payload={"name": "Aarav"}),
#     PointStruct(id=2, vector=embedding_2.data[0].embedding, payload={"name": "Tom"}),
#     PointStruct(id=3, vector=embedding_3.data[0].embedding, payload={"name": "Jack"})
#
# ])
embedding_question = openai.embeddings.create(
    model="text-embedding-ada-002",
    input="",
    encoding_format="float"
)

search_result = client.query_points(
    collection_name="openai",
    query=embedding_question.data[0].embedding,
    limit=1
)

print(search_result)