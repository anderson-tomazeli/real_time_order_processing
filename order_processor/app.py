from src import utils
import pika
import json
import pymongo
import logging

config = utils.get_config()
logger = utils.setup_logging(config)
rabbitmq_config = utils.load_config(config, 'RABBITMQ')

# RabbitMQ connection parameters
rabbitmq_host = rabbitmq_config['rabbitmq_host'] #"rabbitmq"  # Use the service name from Docker Compose
rabbitmq_port = rabbitmq_config['rabbitmq_port'] #5672
orders_queue = rabbitmq_config['orders_queue'] #"orders"
confirmations_queue = rabbitmq_config['confirmations_queue'] #"confirmations"
rabbitmq_user = rabbitmq_config['rabbitmq_user']
rabbitmq_password = rabbitmq_config['rabbitmq_password']

# MongoDB connection parameters
mongodb_config = utils.load_config(config, 'MONGODB')
mongo_host = mongodb_config['mongo_host'] #"mongodb"  # Use the service name from Docker Compose
mongo_port = mongodb_config['mongo_port'] #"27017
mongo_db_name = mongodb_config['mongo_db_name'] #""order_db"
mongo_collection_name = mongodb_config['mongo_collection_name'] #""orders"

try:
    # RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)))
    channel = connection.channel()
    channel.queue_declare(queue=orders_queue)
    channel.queue_declare(queue=confirmations_queue) #, durable=True)

    # MongoDB connection
    mongo_client = pymongo.MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")
    mongo_db = mongo_client[mongo_db_name]
    mongo_collection = mongo_db[mongo_collection_name]

    def process_order(order_data):
        try:
            logger.info(f"Processing order: {order_data}")

            # Store order in MongoDB
            mongo_collection.insert_one(order_data)
            logger.info(f"Order stored in MongoDB: {order_data['order_id']}")

            # Basic order validation (example)
            if not order_data.get("product"):
                #raise ValueError("Product is required")
                try:
                    raise ValueError("Product is required")  # Raise the exception
                except ValueError as e:
                    logger.exception("Error processing order: %s", e) # Log the exception
                    raise  # Re-raise the exception (optional, but often good practice)

            # Send confirmation message
            confirmation_message = {"order_id": order_data["order_id"], "status": "confirmed"}
            channel.basic_publish(exchange='', routing_key=confirmations_queue, properties=pika.BasicProperties(delivery_mode=2), body=json.dumps(confirmation_message))
            logger.info(f"Confirmation sent for order: {order_data['order_id']}")

        except pymongo.errors.ConnectionFailure as e:
            logger.error(f"MongoDB connection error: {e}")
            # Requeue the message for later processing (optional)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except ValueError as e:
            logger.error(f"Order validation error: {e}")
            confirmation_message = {"order_id": order_data["order_id"], "status": "failed", "error": str(e)}
            channel.basic_publish(exchange='', routing_key=confirmations_queue, body=json.dumps(confirmation_message))
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            # Requeue the message (optional)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def callback(ch, method, properties, body):
        try:
            order_data = json.loads(body)
            process_order(order_data)
            ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message after successful processing
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Reject message if it's not a valid JSON

    channel.basic_consume(queue=orders_queue, on_message_callback=callback)

    print(' [*] Waiting for order messages. To exit press CTRL+C')
    channel.start_consuming() # This line keeps the script running

except pika.exceptions.AMQPConnectionError as e:
    logger.error(f"RabbitMQ connection error: {e}")
except pymongo.errors.ConnectionFailure as e:
    logger.error(f"MongoDB connection error: {e}")
except Exception as e:
    logger.error(f"An error occurred: {e}")
