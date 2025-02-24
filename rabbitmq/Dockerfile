# Use the management image to easily add users
#FROM rabbitmq:3.9-management  
FROM rabbitmq:3.13-management  

COPY rabbitmq_user_setup.sh /docker-entrypoint-initdb.d/

# Make the script executable
RUN chmod +x /docker-entrypoint-initdb.d/rabbitmq_user_setup.sh

# Expose the RabbitMQ management port (optional, but useful)
EXPOSE 15672

# Expose the RabbitMQ AMQP port
EXPOSE 5672

# You can add other configurations here if needed, like setting up plugins.
