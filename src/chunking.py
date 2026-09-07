import re

#para hacer chunks de un tamaño aceptable, como procesamos markdown, lo hacemos por cada "##"
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


if __name__ == "__main__":
    with open("knowledge/runbooks/redis.md", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_markdown(text)

    print(f"Total de chunks generados: {len(chunks)}\n")

    for i, chunk in enumerate(chunks, start=1):
        print(f"Chunk {i}:\n{chunk}\n")
    