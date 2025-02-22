import asyncio
import json
from contextlib import asynccontextmanager
import redis.asyncio as redis
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
REDIS_PSW = os.getenv('REDIS_PSW')
try:
    HOST = os.getenv('HOST')
except Exception:
    HOST = 'localhost'


@asynccontextmanager
async def redis_conn():
    connection = redis.from_url(f"redis://default:{REDIS_PSW}@{HOST}:6379/3", encoding="utf8", decode_responses=True)
    try:
        yield connection
    finally:
        await connection.aclose()


async def redis_add_answer(key: int, value: dict) -> bool:
    """
    Запись ответа
    """
    try:
        async with redis_conn() as r:
            await r.rpush(f'chat_history_{key}', json.dumps(value))
            return True
    except Exception:
        return False


async def redis_get_all_answers(key: int) -> list | bool:
    """
    Считываение всех ответов
    """
    try:
        async with redis_conn() as r:
            items_json = await r.lrange(f'chat_history_{key}', 0, -1)
            items = [json.loads(item) for item in items_json]
            return items
    except Exception:
        traceback.print_exc()
        return False


async def redis_counter_plus(key: int) -> int | bool:
    """
    Добавление счетчика
    """
    try:
        async with redis_conn() as r:
            counter_num = await r.get(f'counter_{key}')
            if counter_num is None:
                counter_num = -1
            counter_num_upd = int(counter_num) + 1
            await r.set(f'counter_{key}', str(counter_num_upd))
            return counter_num_upd
    except Exception:
        return False


async def redis_counter_reset(key: int) -> bool:
    """
    Обнуление счетчика
    """
    try:
        async with redis_conn() as r:
            await r.set(f'counter_{key}', '0')
            return True
    except Exception:
        return False


if __name__ == '__main__':
    pass
