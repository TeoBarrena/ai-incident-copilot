from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import ollama
from pathlib import Path

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

#chunkeo de documento markdown en secciones
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

#Leer los documentos
documents = Path("knowledge/runbooks").rglob("*.md")

point_id = 0

for document in documents:

    with open(document, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_markdown(text) #chunking del documento en secciones

    for chunk_id, chunk in enumerate(chunks):
    
        #Generar el embedding
        response = ollama.embed(
            model="qwen3-embedding:0.6b",
            input=chunk
        )

        embedding = response["embeddings"][0]

        #Metadata del chunk
        payload = {
            "source": document.name,
            "path": str(document),
            "type": document.parent.name,
            "chunk_id": chunk_id,
            "content": chunk
        }

        #Guardar el punto en Qdrant
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        print(f"Chunk {chunk_id} insertado con contenido {chunk}")

        point_id += 1

print(f"\nTodos los chunks insertados en la colección '{collection_name}'")

client.close()


