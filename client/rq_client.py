import os
from dotenv import load_dotenv
from redis import Redis
from rq import Queue

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

redis_conn = Redis(
    host=redis_host,
    port=redis_port
)

queue = Queue("default", connection=redis_conn)