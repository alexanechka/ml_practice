import pika
import json
import datetime
from database.config import get_settings

settings = get_settings()

QUEUE_NAME = "ml_tasks"


def _get_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials,
    )
    return pika.BlockingConnection(parameters)


def publish_task(
    task_id: str, user_id: int, input_data: str, model: str = "summarization"
) -> None:
    message = {
        "task_id": task_id,
        "features": {"input_data": input_data},
        "model": model,
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }

    connection = _get_connection()
    try:
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )

    finally:
        connection.close()
