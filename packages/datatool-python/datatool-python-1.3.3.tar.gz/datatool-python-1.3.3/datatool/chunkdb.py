import os
import re

import pandas as pd

from .mapreduce import mapreduce_multi, THREADS_NUM_DEFAULT


CHUNK_TEMPLATE = "chunk-{}.pkl"
CHUNK_REGEX = re.compile(CHUNK_TEMPLATE.format(r"(\d+)"))


class ChunkTable:
    """
    This class represents a way to store data of a big table
    as a number of chunks that are pandas dataframes.

    Example:

        items_table = ChunkTable("/some/path", "items")

        items_table.size()  # Count of chunks
        items_table.check(100)  # Check if chunk_id=100 exists
        items_table.get_chunks()  # Get list of chunks
        items_table.get(100)  # Get dataframe with chunk_id=100
        items_table.put(df, 101)  # Create dataframe with chunk_id=101
        items_table.save(df, 101)  # Update dataframe with chunk_id=101
        items_table.drop(101)  # Drop dataframe with chunk_id=101
    """

    def __init__(self, path, table):
        self._table_path = os.path.join(path, table)
        self._ensure_table_dir()

    def __repr__(self):
        return f"ChunkTable(table_path={self._table_path})"

    def check(self, chunk_id):
        """
        Checks whether chunk exists with given chunk_id.
        """
        # Get path of the file
        path = self.get_file_path(chunk_id)

        # Return True if chunk exists else False
        return os.path.exists(path)

    def get(self, chunk_id):
        """
        Gets dataframe by given chunk_id.
        """
        # Get path of the file
        path = self.get_file_path(chunk_id)

        # If chunk does not exist raise FileNotFoundError
        if not os.path.exists(path):
            raise FileNotFoundError(f"Chunk {chunk_id} does not exist")

        # Return the dataframe
        return pd.read_pickle(path)

    def put(self, df, chunk_id, quiet=False):
        """
        Puts dataframe chunk to the table.
        If quiet is True, no exception is raised if file already exists.
        """
        # Get path of the file
        path = self.get_file_path(chunk_id)

        # If chunk already exists raise FileExistsError
        if not quiet and os.path.exists(path):
            raise FileExistsError(f"Chunk {chunk_id} already exists")

        # Save the given dataframe to pickle
        df.to_pickle(path)

    def save(self, df, chunk_id):
        """
        Puts or updates the dataframe chunk.
        It is the same as put(df, chunk_id, quiet=True).
        """
        self.put(df, chunk_id, quiet=True)

    def drop(self, chunk_id):
        """
        Drops chunk by given chunk_id.
        """
        # Get path of the file
        path = self.get_file_path(chunk_id)

        # If chunk does not exist raise FileNotFoundError
        if not os.path.exists(path):
            raise FileNotFoundError(f"Chunk {chunk_id} does not exist")

        # Delete the file
        os.remove(path)

    def get_file_path(self, chunk_id):
        """
        Gets path to the chunk file.
        """
        # Check the given chunk_id is integer
        assert isinstance(chunk_id, int), "chunk_id must be integer"

        # Get name of the pickle file
        name = CHUNK_TEMPLATE.format(chunk_id)

        # Return the path to the file
        return os.path.join(self._table_path, name)

    def get_chunks(self):
        """
        Gets id of all saved chunks. The returned list is sorted.
        """
        # Get file names
        filenames = os.listdir(self._table_path)

        # Extract chunk id list
        chunk_id_list = [
            int(CHUNK_REGEX.match(filename).group(1))
            for filename in filenames
        ]

        # Sorting
        chunk_id_list.sort()

        # Return chunk id list
        return chunk_id_list

    def size(self):
        """
        Gets the number of chunks.
        """
        # Get file names
        filenames = os.listdir(self._table_path)

        # Return the count of file names
        return len(filenames)

    def mapreduce(self, map_func, reduce_func,
                  threads_num=THREADS_NUM_DEFAULT, verbose=False):
        """
        Applyis map-reduce over the chunks in the table.
        """
        return mapreduce_multi(
            self.get_chunks(),
            map_func=lambda chunk_id: map_func(self.get(chunk_id)),
            reduce_func=reduce_func,
            threads_num=threads_num,
            verbose=verbose
        )

    def _ensure_table_dir(self):
        if not os.path.exists(self._table_path):
            os.mkdir(self._table_path)
