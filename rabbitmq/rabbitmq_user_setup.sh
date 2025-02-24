#!/bin/bash

# Wait for RabbitMQ to be ready
rabbitmq-ctl wait_for_running

# Create the user
rabbitmqctl add_user order_admin mypasswd

# Set user tags (if needed, e.g., for management access)
#rabbitmqctl set_user_tags order_admin administrator  # Optional: Grant admin privileges
rabbitmqctl set_user_tags order_admin management  # Optional: Grant admin privileges

# Grant permissions to the 'orders' queue (replace with your queue name)
#rabbitmqctl set_permissions -p / order_admin ".*" ".*" ".*"  # Full access to all queues in the default vhost

# Or, for more specific permissions (recommended):
rabbitmqctl set_permissions -p / order_admin "^orders$" "^orders$" "^orders$" # Configure permissions for orders queue only
rabbitmqctl set_permissions -p / order_admin "^confirmation$" "^confirmation$" "^confirmation$" # Configure permissions for orders queue only

echo "RabbitMQ user 'order_admin' created and permissions set."
