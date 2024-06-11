import os
import sys
import asyncio
import json
from job_ingestion import WeaviateIngestion
rpath = os.path.abspath('..')
if rpath not in sys.path:
    sys.path.insert(0, rpath)
from weaviate_helper import setup_weaviate_interface_async


async def main():
    with open('json/job_schema.json', 'r') as f:
        class_definitions = json.load(f)

    with open('json/config.json', 'r') as f:
        config = json.load(f)

    interface = await setup_weaviate_interface_async()
    weaviate_ingestion = WeaviateIngestion(
                            interface,
                            config['chunk_size'],
                            config['batch_size'])

    await weaviate_ingestion.delete_class("Job")
    await weaviate_ingestion.create_class(class_definitions["Job"])
    await weaviate_ingestion.delete_class("JobDescriptionChunk")
    await weaviate_ingestion.create_class(
        class_definitions["JobDescriptionChunk"])

    await weaviate_ingestion.populate_database(config['csv_file_path'])

if __name__ == "__main__":
    asyncio.run(main())
