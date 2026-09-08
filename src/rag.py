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

    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=top_k
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



if __name__ == "__main__":

    query = "¿Qué hago si Redis está usando demasiada memoria?"

    results = retrieve(query)

    answer = generate_answer(query, results)

    print(f"Pregunta: {query}\n")
    print(f"Respuesta: {answer}\n")

    query = "¿En qué puerto funciona Redis?"

    results = retrieve(query)
    
    answer = generate_answer(query, results)

    print(f"Pregunta: {query}\n")
    print(f"Respuesta: {answer}\n")

    query = "¿Cómo configuro Redis Cluster?"

    results = retrieve(query)
        
    answer = generate_answer(query, results)

    print(f"Pregunta: {query}\n")
    print(f"Respuesta: {answer}\n")

    client.close()  
