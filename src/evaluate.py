import ollama

from qdrant_client import QdrantClient


client = QdrantClient(path="qdrant_data")

collection_name = "knowledge"


def retrieve(query, limit=3):

    response = ollama.embed(
        model="qwen3-embedding:0.6b",
        input=query
    )

    query_embedding = response["embeddings"][0]

    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=limit
    ).points

    return results


# Preguntas de evaluación
test_cases = [
    {
        "question": "¿Qué hago si Redis tiene connection timeout?",
        "expected_source": "redis.md"
    },
    {
        "question": "¿Cómo soluciono problemas de memoria en Redis?",
        "expected_source": "redis.md"
    },
    {
        "question": "¿Qué hago si PostgreSQL rechaza las conexiones?",
        "expected_source": "postgresql.md"
    },
    {
        "question": "¿Cómo investigo queries lentas en PostgreSQL?",
        "expected_source": "postgresql.md"
    },
    {
        "question": "¿Qué hago si tengo consumer lag en Kafka?",
        "expected_source": "kafka.md"
    },
    {
        "question": "¿Qué revisar si un broker de Kafka está caído?",
        "expected_source": "kafka.md"
    },
    {
        "question": "¿Cómo configuro Redis Cluster?",
        "expected_source": None
    },
    {
        "question": "¿Cómo hago un backup de PostgreSQL?",
        "expected_source": None
    }
]


correct = 0

print("=" * 70)
print("EVALUACIÓN DEL RETRIEVAL")
print("=" * 70)


for i, test in enumerate(test_cases, start=1):

    question = test["question"]
    expected_source = test["expected_source"]

    results = retrieve(question)

    top_result = results[0]

    source = top_result.payload["source"]
    score = top_result.score

    if expected_source is None:
        status = "N/A"
    elif source == expected_source:
        status = "OK"
        correct += 1
    else:
        status = "ERROR"

    print(f"\nPregunta {i}: {question}")
    print(f"Esperado: {expected_source}")
    print(f"Encontrado: {source}")
    print(f"Score: {score:.4f}")
    print(f"Resultado: {status}")


print("\n" + "=" * 70)

total_with_expected = sum(
    1 for test in test_cases
    if test["expected_source"] is not None
)

accuracy = correct / total_with_expected

print(f"Preguntas evaluables: {total_with_expected}")
print(f"Correctas: {correct}")
print(f"Accuracy del retrieval: {accuracy:.2%}")

client.close()