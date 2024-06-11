from .openai_helper import generate_response
from .job_query import WeaviateQuery
from .weaviate_client_helper import setup_weaviate_interface


async def process_user_query(user_question: str) -> str:
    client = setup_weaviate_interface()
    weaviate_query = WeaviateQuery(client)

    job_results = (
            client.query
            .get("Job", ["job_id", "title", "company"])
            .with_near_text(
                {
                    "concepts": [f"{user_question}"]
                }
            )
            .with_limit(10)
            .with_additional(["distance"])
    ).do()

    prompt = weaviate_query.get_prompt(user_question, job_results)
    response = generate_response(prompt)
    return response
