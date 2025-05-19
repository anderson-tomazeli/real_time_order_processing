🚀 How It Works
Once all containers are up and running smoothly, the magic begins!

The core idea is to generate .json purchase orders inside the orders folder by running the generate_orders.py script located in the root of the project. This script continuously creates random order files to simulate real-world input.

Here’s a quick overview of what happens behind the scenes:

📁 Order Generation
New .json files with random order details are created in the orders folder.

👀 Watchdog Detection
A watchdog service monitors the folder for any new files. When it detects one, it sends a message to the orders queue via RabbitMQ.

⚙️ Order Processing
The order_processor service picks up the message from the orders queue, processes the order, and attempts to store it in the MongoDB container.

✅ If the order is valid, it moves on and sends a message to the confirmations queue.

❌ If there's an issue (e.g., an unavailable product), the .json file stays in the orders folder, an error is logged, and the problematic data is forwarded to the fails queue.

✉️ Notifications
The notification-service listens to the confirmations queue and handles the final step of the workflow.

📝 Logs for Everything
Every step is logged in ./logs/app.log, so you can always track what’s happening in the system.

💡 A Note from the Developer
This is one of my first hands-on projects in data engineering, designed to help me learn by doing. As a next step, I plan to refactor the codebase to follow Object-Oriented Design (OOD) principles—bringing more structure, reusability, and maintainability to the solution.
