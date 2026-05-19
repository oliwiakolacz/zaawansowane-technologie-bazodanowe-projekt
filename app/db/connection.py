from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

import pyodbc

from config import DatabaseConfig


class ConnectionManager:
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self._config = config or DatabaseConfig.from_env()

    @contextmanager
    def get_connection(self) -> Iterator[pyodbc.Connection]:
        conn = pyodbc.connect(self._config.connection_string())
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Iterator[pyodbc.Cursor]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    @contextmanager
    def query(self) -> Iterator[pyodbc.Cursor]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def test_connection(self) -> bool:
        try:
            with self.query() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return True
        except pyodbc.Error:
            return False
