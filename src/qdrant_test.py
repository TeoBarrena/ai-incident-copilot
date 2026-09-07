from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import ollama

client = QdrantClient(path="qdrant_data") #inicializa el cliente de Qdrant

collection_name="knowledge" #nombre de la colección donde se guardarán los embeddings

if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=1024, #tamaño del vector de embeddings, debe coincidir con el tamaño del vector generado por el modelo de embeddings
        distance=Distance.COSINE #tipo de distancia para calcular la similitud entre vectores
    )
)

def chunk_markdown(text):
    lines = text.splitlines()

    title = ""
    sections = []
    current_section = []

    for line in lines:
        # Detectar título principal
        if line.startswith("# ") and not title:
            title = line

        # Detectar secciones
        elif line.startswith("## "):
            if current_section:
                sections.append(current_section)

            current_section = [line]

        elif current_section:
            current_section.append(line)

    if current_section:
        sections.append(current_section)

    chunks = []

    for section in sections:
        content = "\n".join(section).strip()

        chunk = f"{title}\n\n{content}"
        chunks.append(chunk)

    return chunks

#Leer nuestro documento
with open("knowledge/runbooks/redis.md", "r", encoding="utf-8") as file:
    text = file.read()

chunks = chunk_markdown(text) #chunking del documento en secciones

for chunk_id, chunk in enumerate(chunks):

    print(f"Procesando chunk {chunk_id}...")


    #Generar el embedding
    response = ollama.embed(
        model="qwen3-embedding:0.6b",
        input=chunk
    )

    embedding = response["embeddings"][0]

    #Crear un punto para Qdrant, un punto es un vector de embeddings con un ID y un payload (información adicional)
    point = PointStruct(    
        id = chunk_id,
        vector = embedding,
        payload = {
            "source": "redis.md",
            "type": "runbook",
            "chunk_id": chunk_id,
            "content": chunk
        }
    )

    #Guardar el punto en Qdrant
    client.upsert(
        collection_name=collection_name,
        points=[point]
    )

    print(f"Chunk {chunk_id} insertado con contenido {chunk}")

print(f"\nTodos los chunks insertados en la colección '{collection_name}'")

client.close()


