from src import utils
import pika
import json
import uuid  # For generating unique order IDs
import sys
#print(sys.path)

config = utils.get_config()
logger = utils.setup_logging(config)
rabbitmq_config = utils.load_config(config, 'RABBITMQ')

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
        logger.info(f"Order placed: {order_data}")

        connection.close()
    except Exception as e:
        logger.exception(f"Error placing order: {e}")

# Example usage:
order1 = {
    "customer_id": "123",
    "product": "Laptop",
    "quantity": 1
}

order2 = {
    "customer_id": "456",
    "product": "Mouse",
    "quantity": 2
}

place_order(order1)
place_order(order2)
