import chromadb
import tiktoken

# Инициализация векторной базы ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="latoken_info")

# Разбиение текста на части (например, предложения или абзацы)
def split_text(text, max_tokens=1000):
    # Используем tiktoken для подсчета токенов
    enc = tiktoken.get_encoding("cl100k_base")
    words = text.split()
    current_chunk = []
    current_length = 0
    chunks = []

    for word in words:
        token_count = len(enc.encode(word))
        if current_length + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = token_count
        else:
            current_chunk.append(word)
            current_length += token_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def upload_from_file(filename: str):
    # Пример текста
    with open(filename) as f:
        text = f.read()

    # Разбиение текста на части и добавление в базу данных
    chunks = split_text(text)

    for chunk in chunks:
        collection.add(
            documents=[chunk],
            metadatas=[{"source": "document"}],
            ids=[str(hash(chunk))],
        )


if __name__ == '__main__':
    pass
