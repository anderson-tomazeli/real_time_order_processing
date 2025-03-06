# order-processor/test_app.py  (Create a new file for tests)
import unittest
import json
from unittest.mock import patch, MagicMock  # For mocking external dependencies
from app import process_order  # Import the function you want to test

class TestOrderProcessor(unittest.TestCase):

    @patch('app.mongo_collection')  # Mock MongoDB interaction
    @patch('app.channel')  # Mock RabbitMQ interaction
    def test_process_order_valid_order(self, mock_channel, mock_collection):
        order_data = {
            "order_id": "test_id",
            "customer_id": "123",
            "product": "Laptop",
            "quantity": 1
        }

        process_order(order_data)

        mock_collection.insert_one.assert_called_once_with(order_data)  # Check MongoDB interaction
        mock_channel.basic_publish.assert_called_once()  # Check RabbitMQ confirmation

    @patch('app.mongo_collection')
    @patch('app.channel')
    def test_process_order_invalid_order(self, mock_channel, mock_collection):
        order_data = {  # Missing required fields
            "customer_id": "123",
            "product": "Laptop",
            "quantity": 1
        }

        process_order(order_data)

        mock_collection.insert_one.assert_not_called()  # Shouldn't interact with MongoDB
        mock_channel.basic_publish.assert_not_called()  # Shouldn't send confirmation

    # ... more test cases ...

if __name__ == '__main__':
    unittest.main()
