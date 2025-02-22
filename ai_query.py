import os
from openai import AsyncOpenAI
import chromadb
from dotenv import load_dotenv
from redis_handler import redis_add_answer, redis_get_all_answers, redis_counter_plus, redis_counter_reset


load_dotenv()


# Инициализация векторной базы ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="latoken_info")
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Запоминаем историю сообщений
# chat_history = []
# ask_counter = 0


# Функция для получения данных из ChromaDB
def fetch_data_from_chromadb(query: str, top_k: int = 10):
    results = collection.query(query_texts=[query], n_results=top_k)
    main_result = ''
    for row_list in results['documents']:
        for row in row_list:
            main_result += f'{row}\n'
    return main_result


async def ai_generate_answer(context: str, query: str, tg_id: int) -> str:
    """
    # Функция для генерации ответа с использованием GPT-4
    """
    # global ask_counter
    ask_counter = await redis_counter_plus(tg_id)
    chat_history = await redis_get_all_answers(tg_id)
    question = False

    client = AsyncOpenAI(api_key=os.getenv('OPENAI_TOKEN'))
    if ask_counter <= 2 and len(chat_history) <= 2:
        messages = [
            {"role": "system",
             "content": "You only answer about the company based on the context. Answer as briefly as possible and rephrase so that it is also related in Russian. Offer to tell about the company, about the hackathon or the company culture if it has not been told yet."},
        ]
    elif ask_counter == 1:
        messages = [
            {"role": "system",
             "content": "Tell me whether the answer to the previous question was correct based on the context data. Answer in Russian"},
        ]
    elif ask_counter >= 3:
        messages = [
            {"role": "system",
             "content": "You answer only about the company, based on the context. Answer as briefly as possible and rephrase so that it is related in Russian. Immediately after answering the question, ask a question in the form of a test (2-4 answer options), based only on the information of all the answers you gave earlier. Questions should not be repeated in context."},
        ]
        await redis_counter_reset(tg_id)
        question = True
    else:
        messages = [
            {"role": "system",
             "content": "You only answer about the company based on the context. Answer as briefly as possible and rephrase it so that it is related and in Russian."},
        ]

    # Добавляем историю сообщений, если она есть
    for message in chat_history:
        messages.append(message)

    if question:
        query += 'Задай мне вопрос в виде теста, чтобы проверить мои знания по твоим ответам выше'
    # Добавляем новое сообщение от пользователя и контекст
    messages.append({"role": "user", "content": query})
    messages.append({"role": "assistant", "content": context})

    response = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        max_tokens=8000,
        temperature=0.4
    )

    # Получаем и возвращаем ответ
    answer = response.choices[0].message.content
    # Запоминаем ответ модели в истории
    # chat_history.append({"role": "assistant", "content": answer})
    await redis_add_answer(tg_id, {"role": "assistant", "content": answer})

    return answer


# Основной метод для обработки запросов
async def ai_answer_query(query: str, tg_id: int) -> str:
    # Получаем данные из ChromaDB
    context = fetch_data_from_chromadb(query)
    # print(context)

    # Генерируем ответ с использованием GPT-4
    answer = await ai_generate_answer(context, query, tg_id)
    return answer
