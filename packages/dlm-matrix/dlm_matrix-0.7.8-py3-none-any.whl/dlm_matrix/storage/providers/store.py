from typing import Type, List, Optional, Dict, Any, Union, Set, Iterator
from dlm_matrix.type import NodeRelationship
from pydantic import BaseModel, Field
import pandas as pd
import sqlite3
import json
from dlm_matrix.models import Chain
import uuid


def get_new_id(existing_ids: Set[str]) -> str:
    """Get a new ID."""
    new_id = str(uuid.uuid4())
    while new_id in existing_ids:
        new_id = str(uuid.uuid4())
    return new_id


class ChainDocumentStore(BaseModel):
    """Document store."""

    docs: Dict[str, Chain] = Field(
        default_factory=dict,
        description="The documents in the document store.",
    )

    relationships: Dict[str, NodeRelationship] = Field(
        default_factory=dict,
        description="The relationships between documents in the document store.",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document store to a dictionary."""
        return {id: doc.dict() for id, doc in self.docs.items()}

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the document store to a dataframe."""
        return pd.DataFrame.from_dict(self.to_dict(), orient="index")

    def to_csv(self, csv_path: str) -> None:
        """Convert the document store to a CSV file."""
        df = self.to_dataframe()
        df.to_csv(csv_path)

    @classmethod
    def get_value(
        cls, data: Dict, key: str, expected_type: Union[Type, Any], default=None
    ) -> Any:
        """Helper function to get a value from a dictionary, with error handling."""
        value = data.get(key, default)
        if value is not None and not isinstance(value, expected_type):
            raise TypeError(
                f"Expected type {expected_type} for key {key}, but got type {type(value)}"
            )
        return value

    @classmethod
    def from_dict(cls, data: Dict) -> "ChainDocumentStore":
        """Create a ChainDocumentStore from a dictionary."""
        docs = {}
        for id, doc_data in data.items():
            text = cls.get_value(doc_data, "text", str)
            doc = Chain(text=text, id=id)
            doc.children = []
            doc.embedding = cls.get_value(doc_data, "embedding", object)
            doc.annotations = cls.get_value(doc_data, "annotations", object)
            doc.links = cls.get_value(doc_data, "links", object)
            doc.next = cls.get_value(doc_data, "next", str)
            doc.prev = cls.get_value(doc_data, "prev", str)
            children = cls.get_value(doc_data, "children", list)
            for child in children:
                doc.children.append(child)
            docs[id] = doc

        obj = cls()
        obj.docs = docs

        return obj

    @classmethod
    def from_json(
        cls,
        json_path: str,
        db_path: Optional[str] = None,
        table: Optional[str] = None,
    ) -> "ChainDocumentStore":
        """Create from JSON and optionally save to SQLite.

        Args:
            json_path: Path to JSON file.
            db_path: Optional path to SQLite database file. If provided, saves the documents there.
            table: Optional table name for SQLite database. Required if db_path is provided.

        Returns:
            A ChainDocumentStore instance.
        """
        with open(json_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data, db_path, table)

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
    ) -> "ChainDocumentStore":
        """Create from dataframe and optionally save to SQLite.

        Args:
            df: DataFrame of documents.
            db_path: Optional path to SQLite database file. If provided, saves the documents there.
            table: Optional table name for SQLite database. Required if db_path is provided.

        Returns:
            A ChainDocumentStore instance.
        """
        obj = cls()
        for id, row in df.iterrows():
            doc = Chain(**row)
            obj.docs[id] = doc
        return obj

    @classmethod
    def from_csv(
        cls,
        csv_path: str,
        db_path: Optional[str] = None,
        table: Optional[str] = None,
    ) -> "ChainDocumentStore":
        """Create from CSV and optionally save to SQLite.

        Args:
            csv_path: Path to CSV file.
            db_path: Optional path to SQLite database file. If provided, saves the documents there.
            table: Optional table name for SQLite database. Required if db_path is provided.

        Returns:
            A ChainDocumentStore instance.
        """
        df = pd.read_csv(csv_path)
        return cls.from_dataframe(df, db_path, table)

    @classmethod
    def from_documents(
        cls,
        docs: List["Chain"],
        db_path: Optional[str] = None,
        table: Optional[str] = None,
    ) -> "ChainDocumentStore":
        """Create from documents and optionally save to SQLite.

        Args:
            docs: List of ChainDocuments to add to the store.
            db_path: Optional path to SQLite database file. If provided, saves the documents there.
            table: Optional table name for SQLite database. Required if db_path is provided.

        Returns:
            A ChainDocumentStore instance.
        """
        obj = cls()
        obj.add_documents(docs)

        if db_path:
            if not table:
                raise ValueError("Table name must be provided if db_path is specified.")
            obj.to_sqlite(db_path, table)

        return obj

    def to_sqlite(
        self, db_path: str, table: str, df: Optional[pd.DataFrame] = None
    ) -> None:
        """Convert the document store to a SQLite table.

        Args:
            db_path: The path to the SQLite database file.
            table: The name of the table where the data should be inserted.
            df: Optional DataFrame. If not provided, self.to_dataframe() will be used.

        """
        conn = sqlite3.connect(db_path)

        if df is None:
            df = self.to_dataframe()

        df.to_sql(table, conn, if_exists="replace")

    def __iter__(self) -> Iterator[Chain]:
        """Get iterator."""
        return iter(self.docs.values())

    def __len__(self) -> int:
        """Get length."""
        return len(self.docs.keys())

    def get_new_id(self) -> str:
        """Get a new ID."""
        return get_new_id(set(self.docs.keys()))

    def update_docstore(self, other: "ChainDocumentStore") -> None:
        """Update docstore."""
        self.docs.update(other.docs)

    def get_all_documents(self) -> List[Chain]:
        """Get all documents."""
        return list(self.docs.values())

    def add_documents(self, docs: List[Chain], generate_id: bool = False) -> None:
        """Add a document to the store.

        If generate_id = True, then generate id for doc if id doesn't exist.

        """
        for doc in docs:
            if doc.id is None and generate_id:
                doc.id = self.get_new_id()
            self.docs[doc.id] = doc

    def delete_documents(self, ids: List[str]) -> None:
        """Delete documents."""
        for id in ids:
            del self.docs[id]

    def get_documents(self, ids: List[str]) -> List[Chain]:
        """Get documents from the store."""
        return [self.docs.get(id) for id in ids]

    def get_relationships(self, ids: List[str]) -> List[NodeRelationship]:
        """Get relationships from the store."""
        return [self.relationships.get(id) for id in ids]
