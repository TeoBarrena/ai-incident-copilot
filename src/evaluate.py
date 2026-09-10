import ollama

from qdrant_client import QdrantClient


client = QdrantClient(path="qdrant_data")

collection_name = "knowledge"

score_threshold = 0.54

def retrieve(query, limit=3):

    response = ollama.embed(
        model="qwen3-embedding:0.6b",
        input=query
    )

    query_embedding = response["embeddings"][0]

    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=limit,
        score_threshold=score_threshold
    ).points

    return results


# Preguntas de evaluación
test_cases = [

    # ==========================================================
    # REDIS
    # ==========================================================

    {
        "question": "¿Qué hago si Redis tiene connection timeout?",
        "category": "directa",
        "expected_source": "redis.md",
        "expected_chunk": 0
    },

    {
        "question": "¿Cómo soluciono problemas de memoria en Redis?",
        "category": "directa",
        "expected_source": "redis.md",
        "expected_chunk": 1
    },

    {
        "question": "Redis está consumiendo demasiada memoria, ¿qué debería revisar?",
        "category": "reformulada",
        "expected_source": "redis.md",
        "expected_chunk": 1
    },

    {
        "question": "Mi aplicación pierde la conexión con Redis, ¿qué puedo comprobar?",
        "category": "reformulada",
        "expected_source": "redis.md",
        "expected_chunk": 0
    },

    {
        "question": "Redis no responde a las conexiones.",
        "category": "ambigua",
        "expected_source": "redis.md",
        "expected_chunk": 0
    },

    # ==========================================================
    # POSTGRESQL
    # ==========================================================

    {
        "question": "¿Qué hago si PostgreSQL rechaza las conexiones?",
        "category": "directa",
        "expected_source": "postgresql.md",
        "expected_chunk": 0
    },

    {
        "question": "¿Cómo investigo queries lentas en PostgreSQL?",
        "category": "directa",
        "expected_source": "postgresql.md",
        "expected_chunk": 1
    },

    {
        "question": "Las consultas de PostgreSQL están tardando demasiado, ¿qué debería revisar?",
        "category": "reformulada",
        "expected_source": "postgresql.md",
        "expected_chunk": 1
    },

    {
        "question": "Mi aplicación no puede conectarse a la base de datos PostgreSQL.",
        "category": "reformulada",
        "expected_source": "postgresql.md",
        "expected_chunk": 0
    },

    {
        "question": "PostgreSQL está funcionando pero las consultas tardan mucho.",
        "category": "ambigua",
        "expected_source": "postgresql.md",
        "expected_chunk": 1
    },

    # ==========================================================
    # KAFKA
    # ==========================================================

    {
        "question": "¿Qué hago si tengo consumer lag en Kafka?",
        "category": "directa",
        "expected_source": "kafka.md",
        "expected_chunk": 0
    },

    {
        "question": "¿Qué revisar si un broker de Kafka está caído?",
        "category": "directa",
        "expected_source": "kafka.md",
        "expected_chunk": 1
    },

    {
        "question": "Los mensajes de Kafka se están acumulando, ¿qué debería revisar?",
        "category": "reformulada",
        "expected_source": "kafka.md",
        "expected_chunk": 0
    },

    {
        "question": "Un consumidor de Kafka está procesando mensajes demasiado lentamente.",
        "category": "reformulada",
        "expected_source": "kafka.md",
        "expected_chunk": 0
    },

    {
        "question": "Kafka tiene problemas y no está funcionando correctamente.",
        "category": "ambigua",
        "expected_source": "kafka.md",
        "expected_chunk": [0,1]
    },

    # ==========================================================
    # FUERA DEL CONOCIMIENTO
    # ==========================================================

    {
        "question": "¿Cómo configuro Redis Cluster?",
        "category": "fuera_del_conocimiento",
        "expected_source": None,
        "expected_chunk": None
    },

    {
        "question": "¿Cómo hago un backup de PostgreSQL?",
        "category": "fuera_del_conocimiento",
        "expected_source": None,
        "expected_chunk": None
    },

    {
        "question": "¿Cómo configuro Kafka exactamente una vez?",
        "category": "fuera_del_conocimiento",
        "expected_source": None,
        "expected_chunk": None
    },

    {
        "question": "¿Cómo hago failover de Redis?",
        "category": "fuera_del_conocimiento",
        "expected_source": None,
        "expected_chunk": None
    },

    {
        "question": "¿Cómo configuro replicación en PostgreSQL?",
        "category": "fuera_del_conocimiento",
        "expected_source": None,
        "expected_chunk": None
    }
]


total_correct = 0
total_evaluable = 0

print("=" * 70)
print("EVALUACIÓN DEL RETRIEVAL")
print("=" * 70)


for i, test in enumerate(test_cases, start=1):

    question = test["question"]
    category = test["category"]
    expected_source = test["expected_source"]
    expected_chunk = test["expected_chunk"]

    results = retrieve(question)

    print(f"\nPregunta {i}: {question}")
    print(f"Categoría: {category}")

    if not results:

        print("Resultados recuperados: ninguno")

        if expected_source is None:
            print("Resultado: OK - correctamente descartada")
        else:
            print("Resultado: ERROR - no encontró información esperada")

        continue

    top_result = results[0]

    source = top_result.payload["source"]
    chunk_id = top_result.payload["chunk_id"]
    score = top_result.score

    print(f"Top result: {source}")
    print(f"Chunk: {chunk_id}")
    print(f"Score: {score:.4f}")

    if expected_source is None:

        print("Resultado: REVISAR - encontró información para una pregunta fuera del conocimiento")

    else:

        total_evaluable += 1

        if isinstance(expected_chunk, list):
            chunk_correct = chunk_id in expected_chunk
        else:
            chunk_correct = chunk_id == expected_chunk

        if (
            source == expected_source
            and chunk_correct
        ):
            print("Resultado: OK")
            total_correct += 1
        else:
            print("Resultado: ERROR")


print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)

print(f"Total de preguntas: {len(test_cases)}")
print(f"Preguntas evaluables: {total_evaluable}")
print(f"Correctas: {total_correct}")

if total_evaluable > 0:
    accuracy = total_correct / total_evaluable
    print(f"Top-1 Accuracy: {accuracy:.2%}")

print(f"\nScore threshold utilizado: {score_threshold}")

client.close()