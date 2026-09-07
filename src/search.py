from qdrant_client import QdrantClient
import ollama

client = QdrantClient(path="qdrant_data") #inicializa el cliente de Qdrant

collection_name="knowledge"

#Pregunta random del usuario
query = "¿Qué hago si Redis tiene connection timeout?"

#Generar embedding de la respuesta que luego se usa para comparar y buscar la respuesta en Qdrant
response = ollama.embed(
    model="qwen3-embedding:0.6b",
    input=query
)

query_embedding = response["embeddings"][0]

#Se realiza la búsqueda en Qdrant
results = client.query_points(
    collection_name=collection_name,
    query=query_embedding,
    limit=3 #permite limitar la cantidad de resultados que obtiene la consulta
).points

print(f"Resultados de la búsqueda para la pregunta: '{query}'\n")

for i, result in enumerate(results, start=1):
    print(f"Resultado {i}:")
    print(f"Score: {result.score}")
    print(f"Source: {result.payload['source']}")
    print(f"Content: {result.payload['content']}\n")
    print()

client.close()
