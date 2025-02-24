#!/bin/bash

sleep 5  # Wait for 5 seconds (adjust as needed)

# Make the script executable (good practice)
chmod +x /etc/rabbitmq/rabbitmq_init.sh

# Add the user and set permissions (your existing commands)
rabbitmqctl add_user order_admin mypassword
rabbitmqctl set_user_tags order_admin management
rabbitmqctl set_permissions -p / order_admin ".*" ".*" ".*"

# Any other initialization you need...

echo "RabbitMQ initialization complete."
