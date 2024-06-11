class WeaviateQuery:
    def __init__(self, client):
        self.client = client

    def get_job_description_chunks(self, job_id: str) -> str:
        description_query = (
            self.client.query
            .get("JobDescriptionChunk", ["content"])
            .with_where({
                "path": ["job_id"],
                "operator": "Equal",
                "valueText": job_id
            })
        )
        description_response = description_query.do()
        descriptions = (description_response
                        ['data']['Get']['JobDescriptionChunk'])
        return ''.join(desc['content'].strip() for desc in descriptions)

    def compile_job_descriptions(self, job_results: dict) -> str:
        all_job_context = ""
        for job in job_results['data']['Get']['Job']:
            job_id = job["job_id"]
            title = job.get("title", "")
            company = job.get("company", "")
            description = self.get_job_description_chunks(job_id)
            job_context = (f"Title: {title}\nCompany: {company}\n"
                           f"Description:\n{description}\n---\n")
            all_job_context += job_context
        return all_job_context.rstrip('---\n')

    def get_prompt(self, user_question: str, job_results: dict) -> str:
        all_job_context = self.compile_job_descriptions(job_results)
        final_prompt = f"""
                I have been provided with a set of job descriptions,
                each containing a title, company, and description.

                These descriptions are presented below:\n{all_job_context}

                **[End of Descriptions]**

                \n\nGiven these job descriptions,
                what job description best addresses the following question:\n

                {user_question}"""
        return final_prompt
