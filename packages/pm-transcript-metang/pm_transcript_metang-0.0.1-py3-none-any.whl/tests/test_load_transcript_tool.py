import pytest
import unittest

from promptflow.connections import CustomConnection
from pm_transcript_metang.tools.load_transcript_tool import load_transcript


@pytest.fixture
def my_custom_connection() -> CustomConnection:
    my_custom_connection = CustomConnection(
        {
            "api-key" : "my-api-key",
            "api-secret" : "my-api-secret",
            "api-url" : "my-api-url"
        }
    )
    return my_custom_connection


class TestTool:
    def test_local_transcript(self): #, my_custom_connection):
        result = load_transcript(filepath="Microsoft")
        assert result == "Hello Microsoft"


# Run the unit tests
if __name__ == "__main__":
    unittest.main()