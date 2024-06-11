import pandas as pd
import httpx
from uuid import uuid4
from typing import List


class WeaviateIngestion:
    def __init__(self, interface, chunk_size, batch_size):
        self.interface = interface
        self.chunk_size = chunk_size
        self.batch_size = batch_size

    async def delete_class(self, class_name: str) -> None:
        await self.interface.client.delete_class(class_name=class_name)

    async def create_class(self, class_info: dict) -> None:
        await self.interface.client.create_class(class_info)

    def chunk_text(self, text: str) -> List[str]:
        return [
            text[i:i + self.chunk_size]
            for i in range(0, len(text), self.chunk_size)]

    async def batch_create_objects(
            self, objects: List[dict], 
            class_name: str) -> None:
        for i in range(0, len(objects), self.batch_size):
            batch = objects[i:i + self.batch_size]
            try:
                success = await self.interface.client.batch_create_objects(
                    batch,
                    class_name=class_name
                    )
                if success:
                    print(f"{class_name} batch {i // self.batch_size + 1}"
                          "created successfully")
                else:
                    print(f"{class_name} batch {i // self.batch_size + 1}"
                          "creation failed")
            except httpx.HTTPStatusError as e:
                print(f"HTTP error occurred: {e.response.status_code}"
                      f" - {e.response.text}")
            except Exception as e:
                print(f"An error occurred while creating {class_name}"
                      f"batch objects: {e}")

    async def populate_database(self, csv_file_path: str) -> None:
        df = pd.read_csv(csv_file_path)
        columns_to_keep = ['title', 'company', 'description']
        df_cleaned = df[columns_to_keep].dropna()
        df_cleaned = df_cleaned[(df_cleaned['title'].str.strip() != '') &
                                (df_cleaned['company'].str.strip() != '') &
                                (df_cleaned['description'].str.strip() != '')]

        objects = []
        chunks = []
        for _, row in df_cleaned.iterrows():
            job_id = str(uuid4())
            objects.append({
                "job_id": job_id,
                "title": row.title,
                "company": row.company
            })
            description_chunks = self.chunk_text(row.description)
            for order, chunk in enumerate(description_chunks):
                chunks.append({
                    "job_id": job_id,
                    "content": chunk,
                    "order": order
                })

        await self.batch_create_objects(
            objects,
            class_name="Job")
        await self.batch_create_objects(
            chunks,
            class_name="JobDescriptionChunk")
