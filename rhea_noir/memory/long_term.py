from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import os
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BigQueryMemory")

class BigQueryMemory:
    """
    Long-term memory backed by Google BigQuery.
    Stores extracted facts and context for persistent recall.
    """
    
    def __init__(self, project_id: str = None, location: str = "US"):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.client = None
        self.dataset_id = "rhea_noir"
        self.table_id = "facts"
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._ready = False

    def _get_client(self):
        if not self.client:
            self.client = bigquery.Client(project=self.project_id, location=self.location)
        return self.client

    def initialize(self):
        """Initialize schema (Dataset & Table). Run in background."""
        self._executor.submit(self._ensure_schema)

    def _ensure_schema(self):
        """Ensure dataset and table exist."""
        client = self._get_client()
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        # 1. Create Dataset
        try:
            client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_ref} exists.")
        except NotFound:
            logger.info(f"Creating dataset {dataset_ref}...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = self.location
            client.create_dataset(dataset, timeout=30)
            logger.info(f"Dataset {dataset_ref} created.")

        # 2. Create Table
        table_ref = f"{dataset_ref}.{self.table_id}"
        schema = [
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("category", "STRING", mode="REQUIRED"), # e.g. "user_preference", "biography", "project"
            bigquery.SchemaField("fact", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("source_turn", "STRING", mode="NULLABLE"), # Optional: original text source
        ]
        
        try:
            client.get_table(table_ref)
            logger.info(f"Table {table_ref} exists.")
        except NotFound:
            logger.info(f"Creating table {table_ref}...")
            table = bigquery.Table(table_ref, schema=schema)
            # Partition by day for cost control
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="timestamp"
            )
            client.create_table(table)
            logger.info(f"Table {table_ref} created.")
        
        self._ready = True

    def store_fact(self, fact: str, category: str = "general", source: str = None):
        """Store a fact asynchronously."""
        if not self._ready:
            # If called too early, just schedule it
            pass
        self._executor.submit(self._store_fact_sync, fact, category, source)

    def _store_fact_sync(self, fact: str, category: str, source: str):
        """Sync implementation of store."""
        if not self.project_id: 
            logger.warning("No project ID, skipping BigQuery store.")
            return

        client = self._get_client()
        table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        rows = [{
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "category": category,
            "fact": fact,
            "source_turn": source
        }]
        
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            logger.error(f"Encountered errors while inserting rows: {errors}")
        else:
            logger.info(f"Stored fact: {fact[:50]}...")

    def retrieve_recent(self, limit: int = 5) -> List[str]:
        """Retrieve most recent facts (blocking)."""
        if not self._ready or not self.project_id:
            return []
            
        client = self._get_client()
        query = f"""
            SELECT fact, category 
            FROM `{self.project_id}.{self.dataset_id}.{self.table_id}`
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        try:
            query_job = client.query(query)
            results = query_job.result()
            facts = [f"[{row.category}] {row.fact}" for row in results]
            return facts
        except Exception as e:
            logger.error(f"Failed to retrieve facts: {e}")
            return []
