import pika
import json
import logging
from database.config import get_settings
from database.database import engine
from sqlmodel import Session
from services.crud import ml_task as PredictService

logger = logging.getLogger(__name__)
settings = get_settings()
QUEUE_NAME = "ml_tasks"

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        task_id = data["task_id"]

        with Session(engine) as session:
            result = PredictService.predict(task_id=task_id, session=session)
            logger.info(f"Task {task_id} processed: {result}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=30,
        blocked_connection_timeout=2,
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    logger.info("Worker started, waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
