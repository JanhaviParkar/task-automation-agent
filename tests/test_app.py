import unittest
from unittest.mock import patch
import app


class AgentTests(unittest.TestCase):
    def test_search_rejects_empty_topic(self):
        with self.assertRaises(ValueError):
            app.search_web("   ")

    @patch("app.search_web", return_value="some search results")
    @patch("app.summarize_results", return_value="- One\n- Two\n- Three")
    def test_workflow_calls_search_then_summarize(self, mock_summarize, mock_search):
        output = app.run_agent("sample topic", temperature=0.2)
        self.assertIn("Three", output)
        mock_search.assert_called_once_with("sample topic")
        mock_summarize.assert_called_once_with("sample topic", "some search results", 0.2)


if __name__ == "__main__":
    unittest.main()
