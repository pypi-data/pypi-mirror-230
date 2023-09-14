import unittest
from unittest.mock import patch, Mock
from monsterapi import client

class TestMClient(unittest.TestCase):

    def setUp(self):
        self.client = client()
        self.sample_data = {
            "prompt": "Help with testing"
        }

    @patch("requests.post")
    def test_get_response(self, mock_post):
        mock_post.return_value = Mock(status_code=200)
        mock_post.return_value.json.return_value = {
            "message": "Request accepted successfully",
            "process_id": "536f0e22-d98d-4685-9ae1-7755b70feae5",
            "status_url": "https://api.monsterapi.ai/v1/status/536f0e22-d98d-4685-9ae1-7755b70feae5",
            "callback_url": ""
        }

        response = self.client.get_response("falcon-7b-instruct", self.sample_data)
        self.assertIn("process_id", response)

    @patch("requests.get")
    def test_get_status_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = {
            "process_id": "536f0e22-d98d-4685-9ae1-7755b70feae5",
            "status": "COMPLETED",
            "result": {
                "text": "I am always happy to help with testing."
            },
            "credit_used": 1,
            "overage": 0
        }

        status = self.client.get_status("536f0e22-d98d-4685-9ae1-7755b70feae5")
        self.assertEqual(status["status"], "COMPLETED")

    @patch("requests.get")
    def test_get_status_failure(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        mock_get.return_value.json.return_value = {
            "process_id": "8a2bbeee-3cb4-4306-bd6b-40c560b4c1e0",
            "status": "FAILED",
            "result": {
                "errorMessage": "beam_size parameter must be an integer"
            }
        }

        status = self.client.get_status("8a2bbeee-3cb4-4306-bd6b-40c560b4c1e0")
        self.assertEqual(status["status"], "FAILED")

    @patch("requests.get")
    def test_wait_and_get_result(self, mock_get):
        # Mocking sequence of 'RUNNING' status followed by 'COMPLETED' status
        mock_get.side_effect = [
            Mock(status_code=200, json=lambda: {
                "process_id": "536f0e22-d98d-4685-9ae1-7755b70feae5",
                "status": "RUNNING",
            }),
            Mock(status_code=200, json=lambda: {
                "process_id": "536f0e22-d98d-4685-9ae1-7755b70feae5",
                "status": "COMPLETED",
                "result": {
                    "text": "I am always happy to help with testing."
                },
                "credit_used": 1,
                "overage": 0
            })
        ]

        result = self.client.wait_and_get_result("536f0e22-d98d-4685-9ae1-7755b70feae5", timeout=2)
        self.assertIn("text", result)


if __name__ == "__main__":
    unittest.main()
