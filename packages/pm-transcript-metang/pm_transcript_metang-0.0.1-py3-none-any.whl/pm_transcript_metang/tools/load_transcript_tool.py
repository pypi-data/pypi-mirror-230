from promptflow import tool

@tool
def load_transcript(filepath: str) -> str:
    # Replace with your tool code.
    # Usually connection contains configs to connect to an API.
    # Use CustomConnection is a dict. You can use it like: connection.api_key, connection.api_base
    # Not all tools need a connection. You can remove it if you don't need it.
    print(filepath)
    return "Hello " + filepath