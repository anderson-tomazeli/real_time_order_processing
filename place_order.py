#from src import utils
#from ..src.utils import get_config
import pika
import json
import uuid  # For generating unique order IDs
import sys
import logging
from src.utils import setup_logging, get_config, log_info, log_error, log_exception, get_caller, load_config

config = get_config()
setup_logging(config)

caller = get_caller(__file__)
logger = logging.getLogger(caller)

rabbitmq_config = load_config(config, 'RABBITMQ', logger)

rabbitmq_host = "localhost" #rabbitmq_config['rabbitmq_host']
rabbitmq_port = rabbitmq_config['rabbitmq_port']
queue_name = rabbitmq_config['orders_queue']
rabbitmq_user = rabbitmq_config['rabbitmq_user']
rabbitmq_password = rabbitmq_config['rabbitmq_password']

def place_order(order_data):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)  # Declare the queue (idempotent)

        # Generate a unique order ID
        order_data["order_id"] = str(uuid.uuid4())

        # Convert order data to JSON
        message = json.dumps(order_data)

        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        log_info(f"Order placed: {order_data}", logger)

        connection.close()
    except Exception as e:
        log_exception(f"Error placing order: {e}", logger)

# Example usage:
#order1 = {
#    "customer_id": "123",
#    "product": "Laptop",
#    "quantity": 1
#}

#order2 = {
#    "customer_id": "456",
#    "product": "Mouse",
#    "quantity": 2
#}

order1 = {
    "customer_id": "123",
    "product": "Garrafa de café",
    "quantity": 3
}

place_order(order1)
#place_order(order2)


