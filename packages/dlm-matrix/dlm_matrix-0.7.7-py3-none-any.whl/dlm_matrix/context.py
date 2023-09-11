import pandas as pd
from typing import Optional
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Any, Dict
import fsspec
import os
import json
import glob

DEFAULT_PERSIST_DIR = "/storage"


def get_file_paths(base_persist_dir, title):
    persist_dir = os.path.join(base_persist_dir, str(title))

    return (persist_dir,)


def concat_dirs(dir1: str, dir2: str) -> str:
    """

    Concat dir1 and dir2 while avoiding backslashes when running on windows.
    os.path.join(dir1,dir2) will add a backslash before dir2 if dir1 does not
    end with a slash, so we make sure it does.

    """
    dir1 += "/" if dir1[-1] != "/" else ""
    return os.path.join(dir1, dir2)


class DataFrameStore:
    def __init__(self, df=pd.DataFrame()):
        self.df = df

    def persist(self, persist_path, fs=None):
        """Persist the DataFrame to a file."""
        self.df.to_csv(persist_path, index=False)

    @classmethod
    def from_persist_dir(cls, persist_dir, fs=None):
        """Load the DataFrame from a file."""
        df = pd.read_csv(persist_dir)
        return cls(df=df)

    def to_dict(self):
        return self.df.to_dict()

    @classmethod
    def from_dict(cls, save_dict):
        df = pd.DataFrame(save_dict)
        return cls(df=df)

    def get_df(self):
        return self.df

    def set_df(self, df):
        self.df = df

    def drop_columns(self, columns):
        self.df.drop(columns=columns, inplace=True)

    def drop_rows(self, rows: List[int]):
        self.df.drop(rows, inplace=True)

    def add_column(self, column_name: str, column: List[Any]):
        self.df[column_name] = column

    def add_row(self, row: Dict[str, Any]):
        self.df = self.df.append(row, ignore_index=True)

    def get_column(self, column_name: str) -> List[Any]:
        return self.df[column_name].tolist()

    def get_row(self, row_index: int) -> Dict[str, Any]:
        return self.df.iloc[row_index].to_dict()

    def get_row_by_id(self, row_id: str) -> Dict[str, Any]:
        return self.df[self.df["id"] == row_id].iloc[0].to_dict()

    def get_row_index_by_id(self, row_id: str) -> int:
        return self.df[self.df["id"] == row_id].index[0]

    def get_row_by_index(self, row_index: int) -> Dict[str, Any]:
        return self.df.iloc[row_index].to_dict()


class NumpyStore:
    def __init__(self, array=np.array([])):
        self.array = array

    def persist(self, persist_path, fs=None):
        """Persist the numpy array to a file."""
        np.save(persist_path, self.array)

    @classmethod
    def from_persist_dir(cls, persist_dir, fs=None):
        """Load the numpy array from a file."""
        array = np.load(persist_dir)
        return cls(array=array)

    def to_dict(self):
        return self.array.tolist()

    @classmethod
    def from_dict(cls, save_dict):
        array = np.array(save_dict)
        return cls(array=array)

    def get_array(self):
        return self.array


class JsonStore:
    def __init__(self, json_obj={}):
        self.json_obj = json_obj

    def json_serializer(self, obj):
        """Custom JSON serializer to handle np.int64"""
        if isinstance(obj, np.int64):
            return int(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def persist(self, persist_path, fs=None):
        """Persist the json object to a file."""
        with open(persist_path, "w") as f:
            json.dump(self.json_obj, f, indent=4, default=self.json_serializer)

    @classmethod
    def from_persist_dir(cls, persist_dir, fs=None):
        """Load the json object from a file."""
        with open(persist_dir, "r") as f:
            json_obj = json.load(f)
        return cls(json_obj=json_obj)

    def to_dict(self):
        """Convert the JSON object to a dictionary."""
        return self.json_obj

    @classmethod
    def from_dict(cls, save_dict):
        """Create a JsonStore object from a dictionary."""
        return cls(json_obj=save_dict)

    def get_json_obj(self):
        """Retrieve the JSON object."""
        return self.json_obj



@dataclass
class MultiLevelContext:
    """MultiLevelContext context.

    The MultiLevelContext container is a utility container for storing
    main_df, part_df,result3d.csv and global_embedding.

    It contains the following:

    - main_df_store: DataFrameStore
    - global_embedding_store: NumpyStore
    - conversation_tree_store: JsonStore
    - relationship_store: DataFrameStore

    """

    main_df_store: DataFrameStore
    global_embedding_store: NumpyStore
    conversation_tree_store: JsonStore
    relationship_store: DataFrameStore
    coordinate_tree_store: JsonStore

    @classmethod
    def from_defaults(
        cls,
        main_df_store: Optional[DataFrameStore] = None,
        global_embedding_store: Optional[NumpyStore] = None,
        conversation_tree_store: Optional[JsonStore] = None,
        relationship_store: Optional[DataFrameStore] = None,
        coordinate_tree_store: Optional[JsonStore] = None,
        persist_dir: Optional[str] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "MultiLevelContext":
        """Create a MultiLevelContext from defaults."""

        if persist_dir is None:
            main_df_store = main_df_store or DataFrameStore()
            global_embedding_store = global_embedding_store or NumpyStore()
            conversation_tree_store = conversation_tree_store or JsonStore()
            relationship_store = relationship_store or DataFrameStore()
            coordinate_tree_store = coordinate_tree_store or JsonStore()
        else:
            main_df_store = main_df_store or DataFrameStore.from_persist_dir(
                persist_dir + "/main_df.csv", fs=fs
            )

            global_embedding_store = (
                global_embedding_store
                or NumpyStore.from_persist_dir(
                    persist_dir + "/global_embedding.npy", fs=fs
                )
            )

            conversation_tree_store = (
                conversation_tree_store
                or JsonStore.from_persist_dir(
                    persist_dir + "/conversation_tree.json", fs=fs
                )
            )

            relationship_store = relationship_store or DataFrameStore.from_persist_dir(
                persist_dir + "/relationship.csv", fs=fs
            )

            coordinate_tree_store = coordinate_tree_store or JsonStore.from_persist_dir(
                persist_dir + "/coordinate_tree.json", fs=fs
            )

        return cls(
            main_df_store,
            global_embedding_store,
            conversation_tree_store,
            relationship_store,
            coordinate_tree_store,
        )

    def persist(
        self,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        main_df_fname: str = "main_df.csv",
        global_embedding_fname: str = "global_embedding.npy",
        conversation_tree_fname: str = "conversation_tree.json",
        relationship_fname: str = "relationship.csv",
        coordinate_tree_fname: str = "coordinate_tree.json",
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """Persist the MultiLevelContext."""
        if persist_dir is None:
            raise ValueError("Persist directory path cannot be None.")

        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)

        if fs is not None:
            main_df_path = concat_dirs(persist_dir, main_df_fname)
            global_embedding_path = concat_dirs(persist_dir, global_embedding_fname)
            conversation_tree_path = concat_dirs(persist_dir, conversation_tree_fname)
            relationship_path = concat_dirs(persist_dir, relationship_fname)
            coordinate_tree_path = concat_dirs(persist_dir, coordinate_tree_fname)
        else:
            main_df_path = str(Path(persist_dir) / main_df_fname)
            global_embedding_path = str(Path(persist_dir) / global_embedding_fname)
            conversation_tree_path = str(Path(persist_dir) / conversation_tree_fname)
            relationship_path = str(Path(persist_dir) / relationship_fname)
            coordinate_tree_path = str(Path(persist_dir) / coordinate_tree_fname)

        if self.main_df_store is not None:
            self.main_df_store.persist(persist_path=main_df_path, fs=fs)
        if self.global_embedding_store is not None:
            self.global_embedding_store.persist(
                persist_path=global_embedding_path, fs=fs
            )
        if self.conversation_tree_store is not None:
            self.conversation_tree_store.persist(
                persist_path=conversation_tree_path, fs=fs
            )

        if self.relationship_store is not None:
            self.relationship_store.persist(persist_path=relationship_path, fs=fs)

        if self.coordinate_tree_store is not None:
            self.coordinate_tree_store.persist(persist_path=coordinate_tree_path, fs=fs)

    def to_dict(self) -> dict:
        result = {}
        if self.main_df_store is not None:
            result["main_df"] = self.main_df_store.to_dict()
        if self.global_embedding_store is not None:
            result["global_embedding"] = self.global_embedding_store.array.tolist()
        if self.conversation_tree_store is not None:
            result["conversation_tree"] = self.conversation_tree_store.get_json_obj()
        if self.relationship_store is not None:
            result["relationship"] = self.relationship_store.to_dict()
        if self.coordinate_tree_store is not None:
            result["coordinate_tree"] = self.coordinate_tree_store.get_json_obj()
        return result

    @classmethod
    def from_dict(cls, save_dict: dict) -> "MultiLevelContext":
        """Create a MultiLevelContext from dict."""
        main_df_store = DataFrameStore.from_dict(save_dict["main_df"])
        global_embedding_store = NumpyStore(np.array(save_dict["global_embedding"]))
        conversation_tree_store = JsonStore(save_dict["conversation_tree"])
        relationship_store = DataFrameStore.from_dict(save_dict["relationship"])
        coordinate_tree_store = JsonStore(save_dict["coordinate_tree"])
        return cls(
            main_df_store=main_df_store,
            global_embedding_store=global_embedding_store,
            conversation_tree_store=conversation_tree_store,
            relationship_store=relationship_store,
            coordinate_tree_store=coordinate_tree_store,
        )

    @classmethod
    def from_persist_dir(
        cls,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        main_df_fname: str = "main_df.csv",
        global_embedding_fname: str = "global_embedding.npy",
        conversation_tree_fname: str = "conversation_tree.json",
        relationship_fname: str = "relationship.csv",
        coordinate_tree_fname: str = "coordinate_tree.json",
        idx=1,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "MultiLevelContext":
        """Load the MultiLevelContext from a file."""
        if persist_dir is None:
            raise ValueError("Persist directory path cannot be None.")

        # Using glob to get the subdirectories and assuming the first match is the desired title directory
        title_dirs = glob.glob(f"{persist_dir}/*/")
        if not title_dirs:
            raise ValueError("No subdirectory found in the given persist_dir.")
        full_persist_dir = title_dirs[idx]

        if fs is not None:
            main_df_path = concat_dirs(full_persist_dir, main_df_fname)
            global_embedding_path = concat_dirs(
                full_persist_dir, global_embedding_fname
            )
            conversation_tree_path = concat_dirs(
                full_persist_dir, conversation_tree_fname
            )

            relationship_path = concat_dirs(full_persist_dir, relationship_fname)

            coordinate_tree_path = concat_dirs(full_persist_dir, coordinate_tree_fname)

        else:
            main_df_path = str(Path(full_persist_dir) / main_df_fname)
            global_embedding_path = str(Path(full_persist_dir) / global_embedding_fname)
            conversation_tree_path = str(
                Path(full_persist_dir) / conversation_tree_fname
            )
            relationship_path = str(Path(full_persist_dir) / relationship_fname)

            coordinate_tree_path = str(Path(full_persist_dir) / coordinate_tree_fname)

        main_df_store = DataFrameStore.from_persist_dir(persist_dir=main_df_path, fs=fs)
        global_embedding_store = NumpyStore.from_persist_dir(
            persist_dir=global_embedding_path, fs=fs
        )
        conversation_tree_store = JsonStore.from_persist_dir(
            persist_dir=conversation_tree_path, fs=fs
        )

        relationship_store = DataFrameStore.from_persist_dir(
            persist_dir=relationship_path, fs=fs
        )

        coordinate_tree_store = JsonStore.from_persist_dir(
            persist_dir=coordinate_tree_path, fs=fs
        )

        return cls(
            main_df_store=main_df_store,
            global_embedding_store=global_embedding_store,
            conversation_tree_store=conversation_tree_store,
            relationship_store=relationship_store,
            coordinate_tree_store=coordinate_tree_store,
        )

    @property
    def main_df(self):
        return self.main_df_store.df

    @property
    def global_embedding(self):
        return self.global_embedding_store.array

    @property
    def conversation_tree(self):
        return self.conversation_tree_store.json_obj

    @property
    def relationship(self):
        return self.relationship_store.df

    @property
    def coordinate_tree(self):
        return self.coordinate_tree_store.json_obj
