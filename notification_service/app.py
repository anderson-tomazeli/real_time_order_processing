from src import utils
import pika
import json

config = utils.get_config()
logger = utils.setup_logging(config)
rabbitmq_config = utils.load_config(config, 'RABBITMQ')

# RabbitMQ connection parameters (same as order-processor)
rabbitmq_host = rabbitmq_config['rabbitmq_host'] #"rabbitmq"  # Use the service name from Docker Compose
rabbitmq_port = rabbitmq_config['rabbitmq_port'] #5672
queue_name = rabbitmq_config['confirmations_queue'] #"confirmations" # The queue for confirmation messages
rabbitmq_user = rabbitmq_config['rabbitmq_user']
rabbitmq_password = rabbitmq_config['rabbitmq_password']

def send_notification(order_id, status):
    # Simulate sending a notification (replace with actual notification logic)
    #print(f"Notification: Order {order_id} is {status}")  # For now, just print
    logger.info(f"Notification: Order {order_id} is {status}")  # For now, just print

def callback(ch, method, properties, body):
    try:
        message = json.loads(body)  # Parse JSON message
        order_id = message.get("order_id")
        status = message.get("status")

        if order_id and status:
            send_notification(order_id, status)
        else:
            logger.exception("Invalid confirmation message format")
    except json.JSONDecodeError:
        logger.error("Invalid JSON message")
    except Exception as e:
        logger.error(f"Error processing message: {e}")


try:
    #connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port))
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)  # Declare the queue

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for confirmation messages. To exit press CTRL+C')
    channel.start_consuming() # This line keeps the script running

except pika.exceptions.AMQPConnectionError as e:
    print(f"Error connecting to RabbitMQ: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
