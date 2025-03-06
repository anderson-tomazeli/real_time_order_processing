import logging
import json
import os
import random
import uuid
import time
from datetime import datetime, timedelta
from src.utils import setup_logging, get_config, log_info, log_error, get_caller, nvl #, load_config

config = get_config()
setup_logging(config)

service_name = os.environ.get("SERVICE_NAME")

if service_name:
    logger_name = service_name + ' [S]'
else:
    logger_name = get_caller(__file__) + ' [L]'

logger = logging.getLogger(logger_name)

def generate_order(order_id):
    """Generates a single order JSON."""
    product_names = ["Laptop", "Smartphone", "Tablet", "Headphones", "Keyboard", None]
    customer_ids = [str(uuid.uuid4()) for _ in range(5)]
    order_date = datetime.now() - timedelta(days=random.randint(0, 30))

    order = {
        "order_id": order_id,
        "customer_id": random.choice(customer_ids),
        "product": random.choice(product_names),
        "quantity": random.randint(1, 5),
        "order_date": order_date.isoformat(),
        "total_amount": round(random.uniform(50, 2000), 2),
    }
    return order

def generate_orders_to_folder(num_orders, output_folder="orders"):
    """Generates a specified number of orders and saves them to a folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(num_orders):
        order_id = str(uuid.uuid4())
        order = generate_order(order_id)
        file_path = os.path.join(output_folder, f"order_{order_id}.json")
        with open(file_path, "w") as f:
            json.dump(order, f, indent=4)

if __name__ == "__main__":
#randomly generate orders
    while True:
        quantity_orders = [1, 2, 3, 4, 5, 6]
        num_order = random.choice(quantity_orders)
        generate_orders_to_folder(num_order)
        time.sleep(random.uniform(1, 5))  # Generate orders at random intervals
    #num_orders = int(input("Enter the number of orders to generate: "))
    #generate_orders_to_folder(num_orders)
    #log_info(f"{num_orders} orders generated in the 'orders' folder.", logger)
