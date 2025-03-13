Naturally, after all the containers run with no errors, the main idea is to generate .json files in the "orders" folder with purchase order details by executing the generate_orders.py script in the root project path.

While the script continuously generates random order .json files, the watchdog service is triggered by detecting new files in the orders folder, and it sends a message to the "orders" queue. The order_processor service detects it through a RabbitMQ listening process, catches the order's data, storing it in a MongoDB container. If successfully validated, it sends a message to the confirmations queue. If the validation fails, like an order in which the product was not supplied, the file is kept in the orders folder, the system will register a log with errors, and the payload with the failed .json content is sent to the "fails" queue.

The "notification-service" container sends the confirmation message to the "confirmations" queue, finishing the process.

The entire system events are logged to the ./logs/app.log file, making each step of the solution clear.
