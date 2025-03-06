import pika
import json
import os
import logging
from src.utils import setup_logging, get_config, log_info, log_exception, log_error, get_caller, load_config

config = get_config()
setup_logging(config)

service_name = os.environ.get("SERVICE_NAME")
if service_name:
    logger_name = service_name + ' [S]'
else:
    logger_name = get_caller(__file__) + ' [L]'

logger = logging.getLogger(logger_name)

rabbitmq_config = load_config(config, 'RABBITMQ', logger)

# RabbitMQ connection parameters (same as order-processor)
rabbitmq_host = rabbitmq_config['rabbitmq_host'] #"rabbitmq"  # Use the service name from Docker Compose
rabbitmq_port = rabbitmq_config['rabbitmq_port'] #5672
confirmations_queue = rabbitmq_config['confirmations_queue'] #"confirmations" # The queue for confirmation messages
rabbitmq_user = rabbitmq_config['rabbitmq_user']
rabbitmq_password = rabbitmq_config['rabbitmq_password']

def send_notification(order_id, status):
    log_info(f"Notification: Order {order_id} is {status}", logger)  # For now, just print

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)  # Parse JSON message
        order_id = message.get("order_id")
        status = message.get("status")

        if order_id and status:
            send_notification(order_id, status)
        else:
            log_exception("Invalid confirmation message format", logger)
    except json.JSONDecodeError:
        log_error("Invalid JSON message", logger)
    except Exception as e:
        log_error(f"Error processing message: {e}", logger)

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)))
    channel = connection.channel()

    channel.queue_declare(queue=confirmations_queue)  # Declare the queue

    channel.basic_consume(queue=confirmations_queue, on_message_callback=callback, auto_ack=True)

    log_info('[*] Waiting for confirmation messages. To exit press CTRL+C', logger)
    channel.start_consuming() # This line keeps the script running

except pika.exceptions.AMQPConnectionError as e:
    log_info(f"Error connecting to RabbitMQ: {e}", logger)
except Exception as e:
    log_info(f"An error occurred: {e}", logger)
