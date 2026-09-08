import ollama
from qdrant_client import QdrantClient

client = QdrantClient(path="qdrant_data") #inicializa el cliente de Qdrant

collection_name="knowledge" #nombre de la colección donde se guardarán los embeddings

#devuelve los 3 chunks más relevantes para la query que le pasamos
def retrieve(query, top_k=3):

    #Generar embedding de la query
    response = ollama.embed(
        model="qwen3-embedding:0.6b",
        input=query
    )

    query_embedding = response["embeddings"][0]

    #hace un search en Qdrant con el embedding de la query y devuelve los 3 chunks más relevantes
    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=top_k,
        score_threshold=0.54 #umbral de aceptación de resultados, si el score es menor a 0.54 no se considera relevante
    ).points

    return results

def generate_answer(query, results):

    context = "\n\n".join(
        result.payload['content'] 
        for result in results
    )

    prompt = f"""
    Responde la pregunta utilizando únicamente la información del contexto.

    Si el contexto no contiene suficiente información para responder,
    decí que no hay suficiente información disponible.

    Contexto:
    {context}

    Pregunta:
    {query}
    """

    response = ollama.chat(
        model="llama3:8b",
        messages=[
            {
                "role":"user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


def ask(query):

    print("="*70)
    print(f"PREGUNTA: {query}\n")

    results = retrieve(query)

    if not results:
        print("No se encontraron chunks relevantes.")

        print("\n" + "-" * 70)
        print("RESPUESTA:")
        print("No hay suficiente información disponible para responder esta pregunta.")
        print()

        return

    #Muestra de los 3 chunks más relevantes obtenidos para la query pasada
    for i, result in enumerate(results, start=1):
        print(f"Resultado {i}:")
        print(f"Score: {result.score}")
        print(f"Source: {result.payload['source']}")
        print(f"Path: {result.payload['path']}")
        print(f"Chunk id: {result.payload['chunk_id']}")
        print("\nContenido:")
        print(result.payload['content'])
        print()

    #se le pasa al LLM para que genere una respuesta adecuada al usuario, usando el contexto y los 3 chunks más relevantes
    answer = generate_answer(query, results)

    print("\n" + "-" * 70)
    print("RESPUESTA:")
    print(answer)
    print()


if __name__ == "__main__":

    queries = [
        "¿Qué hago si Redis está usando demasiada memoria?",
        "¿Kafka tiene lag qué puedo hacer?",
        "¿Qué hago si las queries de Postgresql están lentas?",
        "¿Cómo configuro Redis Cluster?",
    ] 

    for query in queries:
        ask(query)

    client.close()  
