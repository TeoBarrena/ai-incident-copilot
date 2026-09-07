import ollama

with open("knowledge/runbooks/redis.md", "r", encoding="utf-8") as f:
    text = f.read() #string de todo el contenido de redis.md

#manda al modelo de embeddings el contenido del documento, este modelo tokeniza las palabras y genera un vector de embeddings para cada palabra
response = ollama.embed(
    model="qwen3-embedding:0.6b",
    input=text
)

embedding = response["embeddings"][0] #obtiene el vector de embeddings

print("Texto: ", text)

print("\nCantidad de dimensiones:", len(embedding)) #imprime la cantidad de dimensiones del vector de embeddings
print("\nPrimeros 10 valores:", embedding[:10])

