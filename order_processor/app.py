import pika
import json
import os
import pymongo
import logging
import traceback
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

# RabbitMQ connection parameters
rabbitmq_host = rabbitmq_config['rabbitmq_host']
rabbitmq_port = rabbitmq_config['rabbitmq_port']
orders_queue = rabbitmq_config['orders_queue']
confirmations_queue = rabbitmq_config['confirmations_queue']
fails_queue = rabbitmq_config['fails_queue']
rabbitmq_user = rabbitmq_config['rabbitmq_user']
rabbitmq_password = rabbitmq_config['rabbitmq_password']

# MongoDB connection parameters
mongodb_config = load_config(config, 'MONGODB', logger)
mongo_host = mongodb_config['mongo_host']
mongo_port = mongodb_config['mongo_port']
mongo_db_name = mongodb_config['mongo_db_name']
mongo_collection_name = mongodb_config['mongo_collection_name']

try:
    # RabbitMQ connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)))
    channel = connection.channel()
    channel.queue_declare(queue=orders_queue)
    channel.queue_declare(queue=confirmations_queue) #, durable=True)
    channel.queue_declare(queue=fails_queue) #, durable=True)

    # MongoDB connection
    mongo_client = pymongo.MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")
    mongo_db = mongo_client[mongo_db_name]
    mongo_collection = mongo_db[mongo_collection_name]

    def process_order(order_data): #, ch, method):
        try:
            log_info(f"Processing order: {order_data}", logger)

            # Basic order validation (example)
            if not order_data.get("product"):
                fail_message = {"order_id": order_data["order_id"], "status": "failed"}
                channel.basic_publish(exchange='', routing_key=fails_queue, properties=pika.BasicProperties(delivery_mode=2), body=json.dumps(fail_message))
                #log_exception(f"Order: {order_data['order_id']}: sent to the ""fails"" queue", logger)
                raise ValueError(f"Order: {order_data['order_id']}: Product is required - Sent to the fails queue")  # Raise the exception
            else:
                # Store order in MongoDB
                mongo_collection.insert_one(order_data)
                log_info(f"Order: {order_data['order_id']}: SUCCESSFULLY stored in MongoDB", logger)

                # Send confirmation message
                confirmation_message = {"order_id": order_data["order_id"], "status": "confirmed"}
                channel.basic_publish(exchange='', routing_key=confirmations_queue, properties=pika.BasicProperties(delivery_mode=2), body=json.dumps(confirmation_message))
                log_info(f"Order: {order_data['order_id']}: SUCCESSFULLY sent to the confirmations queue", logger)

            orders_path =  config.get('DEFAULT', 'orders_path')
            delete_file_in_folder(orders_path, f"order_{order_data['order_id']}.json")

        except pymongo.errors.ConnectionFailure as e:
            log_error(f"MongoDB connection error: {e}", logger)
            # Requeue the message for later processing (optional)
            #ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        except ValueError as e:
            log_error(f"Validation: {e}", logger)
            fail_message = {"order_id": order_data["order_id"], "status": "failed", "error": str(e)}
            channel.basic_publish(exchange='', routing_key=fails_queue, body=json.dumps(fail_message))

        except Exception as e:
            #log_error(f"Error processing order: {e}", logger)
            log_error(f"Error processing order: {e}\n{traceback.format_exc()}", logger)
            # Requeue the message (optional)
            #ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def delete_file_in_folder(folder_path, file_name):
        """
        Deletes file with the given name from the specified folder.

        Args:
            folder_path (str): The path to the folder.
            file_name (str): The name of the file to delete.

        Returns:
            bool: True if the file was deleted successfully, False otherwise.
        """
        file_path = os.path.join(folder_path, file_name)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log_info(f"Removed file {folder_path} {file_name}" , logger)
                return True  # File deleted successfully
            else:
                log_info(f"File not found: {folder_path} {file_name}" , logger)
                return False #File does not exist.

        except OSError as e:
            log_error(f"Error deleting file {file_name}: {e}")
            return False  # Error occurred during deletion
        except Exception as e:
            log_error(f"An unexpected error occured: {e}")
            return False

    def callback(ch, method, properties, body):
        try:
            message = json.loads(body) # Load the entire message
            payload = message.get('payload') # Extract the payload

            #order_data = json.loads(body)
            #process_order(order_data) #, ch, method)
            #ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge message after successful processing

            if payload:
                process_order(payload)  # Pass only the payload to process_order
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                log_error("Payload not found in message", logger)
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) #reject message if payload is missing


        except json.JSONDecodeError:
            log_error("Invalid JSON message received", logger)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False) # Reject message if it's not a valid JSON

    channel.basic_consume(queue=orders_queue, on_message_callback=callback)

    log_info('[*] Waiting for order messages. To exit press CTRL+C', logger)
    channel.start_consuming() # This line keeps the script running

except pika.exceptions.AMQPConnectionError as e:
    log_error(f"RabbitMQ connection error: {e}", logger)
except pymongo.errors.ConnectionFailure as e:
    log_error(f"MongoDB connection error: {e}", logger)
except Exception as e:
    log_error(f"An error occurred: {e}", logger)
