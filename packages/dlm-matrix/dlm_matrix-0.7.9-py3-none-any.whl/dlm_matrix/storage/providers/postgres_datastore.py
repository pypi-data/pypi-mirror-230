import os
from typing import Any, List, Dict
from datetime import datetime
import numpy as np

from psycopg2 import connect
from psycopg2.extras import DictCursor
from pgvector.psycopg2 import register_vector

from dlm_matrix.services.helper import to_unix_timestamp
from dlm_matrix.storage.providers.pgvector_datastoree import PGClient, PgVectorDataStore
from dlm_matrix.models import (
    DocumentMetadataFilter,
)

PG_HOST = os.environ.get("PG_HOST", "localhost")
PG_PORT = int(os.environ.get("PG_PORT", 5432))
PG_DB = os.environ.get("PG_DB", "postgres")
PG_USER = os.environ.get("PG_USER", "postgres")
PG_PASSWORD = os.environ.get("PG_PASSWORD", "postgres")


# class that implements the DataStore interface for Postgres Datastore provider
class PostgresDataStore(PgVectorDataStore):
    def create_db_client(self):
        return PostgresClient()


class PostgresClient(PGClient):
    def __init__(self) -> None:
        super().__init__()
        self.client = connect(
            dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
        )
        register_vector(self.client)

    def __del__(self):
        # close the connection when the client is destroyed
        self.client.close()

    async def upsert(self, table: str, chain_document: Dict[str, Any]):
        """
        Takes in a ChainDocument and inserts it into the table.
        """
        with self.client.cursor() as cur:
            # Add a "created_at" field if it does not exist
            if not chain_document.get("create_time"):
                chain_document["create_time"] = datetime.now()

            # Convert embedding to np.array if it's not already
            if isinstance(chain_document["embedding"], list):
                chain_document["embedding"] = np.array(chain_document["embedding"])

            # SQL Query
            query = f"""INSERT INTO {table} (
                        doc_id, 
                        text, 
                        author, 
                        coordinate, 
                        umap_embeddings, 
                        cluster_label, 
                        embedding, 
                        n_neighbors, 
                        relationships, 
                        create_time) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                    ON CONFLICT (doc_id) 
                    DO UPDATE SET 
                        text = %s, 
                        author = %s, 
                        coordinate = %s, 
                        umap_embeddings = %s, 
                        cluster_label = %s, 
                        embedding = %s, 
                        n_neighbors = %s, 
                        relationships = %s, 
                        create_time = %s"""

            # Values to be inserted or updated
            values = (
                chain_document["doc_id"],
                chain_document["text"],
                chain_document["author"],
                chain_document["coordinate"],
                chain_document["umap_embeddings"],
                chain_document["cluster_label"],
                chain_document["embedding"],
                chain_document["n_neighbors"],
                chain_document["relationships"],
                chain_document["create_time"],
            )

            # Execute SQL query
            cur.execute(
                query, values * 2
            )  # * 2 because we need the same values for both insert and update

            # Commit changes
            self.client.commit()

    async def rpc(self, function_name: str, params: dict[str, Any]):
        """
        Calls a stored procedure in the database with the given parameters.
        """
        data = []
        params["in_embedding"] = np.array(params["in_embedding"])
        with self.client.cursor(cursor_factory=DictCursor) as cur:
            cur.callproc(function_name, params)
            rows = cur.fetchall()
            self.client.commit()
            for row in rows:
                row["created_at"] = to_unix_timestamp(row["created_at"])
                data.append(dict(row))
        return data

    async def delete_like(self, table: str, column: str, pattern: str):
        """
        Deletes rows in the table that match the pattern.
        """
        with self.client.cursor() as cur:
            cur.execute(
                f"DELETE FROM {table} WHERE {column} LIKE %s",
                (f"%{pattern}%",),
            )
            self.client.commit()

    async def delete_in(self, table: str, column: str, ids: List[str]):
        """
        Deletes rows in the table that match the ids.
        """
        with self.client.cursor() as cur:
            cur.execute(
                f"DELETE FROM {table} WHERE {column} IN %s",
                (tuple(ids),),
            )
            self.client.commit()

    async def delete_by_filters(self, table: str, filter: DocumentMetadataFilter):
        """
        Deletes rows in the table that match the filter.
        """

        filters = "WHERE"
        if filter.document_id:
            filters += f" document_id = '{filter.document_id}' AND"
        if filter.source:
            filters += f" source = '{filter.source}' AND"
        if filter.source_id:
            filters += f" source_id = '{filter.source_id}' AND"
        if filter.author:
            filters += f" author = '{filter.author}' AND"
        if filter.start_date:
            filters += f" created_at >= '{filter.start_date}' AND"
        if filter.end_date:
            filters += f" created_at <= '{filter.end_date}' AND"
        filters = filters[:-4]

        with self.client.cursor() as cur:
            cur.execute(f"DELETE FROM {table} {filters}")
            self.client.commit()
