import weaviate
import os


async def setup_weaviate_interface_async():
    client = weaviate.Client(
        url="http://localhost:8080",
        additional_headers={
            "X-OpenAI-API-Key": os.getenv("OPENAI_API_KEY")
        }
    )
    return client


def setup_weaviate_interface():
    client = weaviate.Client(
        url="http://localhost:8080",
        additional_headers={
            "X-OpenAI-API-Key": os.getenv("OPENAI_API_KEY")
        }
    )
    return client
