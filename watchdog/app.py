import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pika
import json
import logging
import os
from src.utils import setup_logging, get_config, log_info, log_error, get_caller, load_config

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
rabbitmq_user = rabbitmq_config['rabbitmq_user']
rabbitmq_password = rabbitmq_config['rabbitmq_password']

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".json"):
            log_info(f"New file detected: {event.src_path}", logger)
            send_trigger_message(event.src_path)  # Send RabbitMQ message

def send_trigger_message(file_path):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host, rabbitmq_port, credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password)))
    channel = connection.channel()
    channel.queue_declare(queue=orders_queue)
    try:
        with open(file_path, 'r') as f:
            file_content = json.load(f)
        message = {"action": "process_json", "file_path": file_path, "payload": file_content} #include file path, and json content
        channel.basic_publish(exchange='', routing_key=orders_queue, body=json.dumps(message))
        log_info(f"JSON file content sent to RabbitMQ: {file_path}", logger)

    except FileNotFoundError:
        log_error(f"Error: JSON file not found: {file_path}", logger)
        message = {"action": "file_not_found", "file_path": file_path}
        channel.basic_publish(exchange='', routing_key=orders_queue, body=json.dumps(message))
    except json.JSONDecodeError:
        log_error(f"Error: Invalid JSON format in file: {file_path}", logger)
        message = {"action": "invalid_json", "file_path": file_path}
        channel.basic_publish(exchange='', routing_key=orders_queue, body=json.dumps(message))
    except Exception as e:
        log_error(f"An unexpected error occurred: {e}", logger)
        message = {"action": "general_error", "file_path": file_path, "error": str(e)}
        channel.basic_publish(exchange='', routing_key=orders_queue, body=json.dumps(message))

    connection.close()

if __name__ == "__main__":
    event_handler = NewFileHandler()
    observer = Observer()
    
    orders_path = config.get('DEFAULT', 'orders_path')
    # Ensure the orders path exists
    if not os.path.exists(orders_path):
        os.makedirs(orders_path)
        log_info(f"Created orders directory: {orders_path}", logger)

    observer.schedule(event_handler, orders_path, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()