import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import pickle
from typing import List, Tuple, Optional, Dict, Any

__version__ = '1.0.0'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncSQLite:
    def __init__(self, db_path: str, max_workers: int = 10, initial_pool_size: int = 5, max_pool_size: int = 20, retry_attempts: int = 3):
        self.db_path = db_path
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._initial_pool_size = initial_pool_size
        self._max_pool_size = max_pool_size
        self._connection_pool = asyncio.Queue(maxsize=max_pool_size)
        self.retry_attempts = retry_attempts
        self._query_cache = {}
        asyncio.create_task(self._initialize_pool())

    async def __aenter__(self):
        await self._initialize_pool()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close_pool()

    async def _initialize_pool(self):
        await asyncio.gather(*[self._add_connection_to_pool() for _ in range(self._initial_pool_size)])

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    async def _add_connection_to_pool(self):
        conn = await self._run_in_executor(self._connect)
        await self._connection_pool.put(conn)
        logger.info(f"Connection added to pool. Active connections: {self._connection_pool.qsize()}")

    async def _get_connection(self) -> sqlite3.Connection:
        if self._connection_pool.empty():
            await self._add_connection_to_pool()
        return await self._connection_pool.get()

    async def _release_connection(self, conn: sqlite3.Connection):
        await self._connection_pool.put(conn)

    async def _run_in_executor(self, func: Any, *args: Any) -> Any:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)

    def _to_dict(self, rows) -> Optional[List[Dict]]:
        return [dict(row) for row in rows] if isinstance(rows, list) else dict(rows) if rows else None

    async def _execute_query(self, query: str, params: Optional[Tuple], fetch_one: bool = False) -> Optional[Dict]:
        cache_key = (query, params)
        if cache_key in self._query_cache:
            return pickle.loads(self._query_cache[cache_key])

        conn = await self._get_connection()
        try:
            cursor = await self._run_in_executor(conn.execute, query, params or ())
            rows = await self._run_in_executor(cursor.fetchone if fetch_one else cursor.fetchall)
            result = self._to_dict(rows)
            self._query_cache[cache_key] = pickle.dumps(result)
            return result
        finally:
            await self._release_connection(conn)

    async def execute(self, query: str, params: Optional[Tuple] = None) -> None:
        conn = await self._get_connection()
        try:
            await self._run_in_executor(conn.execute, query, params or ())
            await self._run_in_executor(conn.commit)
        finally:
            await self._release_connection(conn)

    async def insert(self, table: str, values: Dict[str, Any]) -> None:
        query = f"INSERT INTO {table} ({', '.join(values.keys())}) VALUES ({', '.join(['?' for _ in values])})"
        await self.execute(query, tuple(values.values()))

    async def update(self, table: str, values: Dict[str, Any], where: str, params: Tuple) -> None:
        set_clause = ', '.join(f"{k} = ?" for k in values.keys())
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        await self.execute(query, tuple(values.values()) + params)

    async def delete(self, table: str, where: str, params: Tuple) -> None:
        query = f"DELETE FROM {table} WHERE {where}"
        await self.execute(query, params)

    async def fetchall(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        return await self._execute_query(query, params)

    async def fetchone(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        return await self._execute_query(query, params, fetch_one=True)

    async def transaction(self, queries: List[Tuple[str, Tuple]], attempt: int = 0) -> None:
        if attempt >= self.retry_attempts:
            raise RuntimeError("Max transaction attempts exceeded.")

        conn = await self._get_connection()
        try:
            for query, params in queries:
                await self._run_in_executor(conn.execute, query, params)
            await self._run_in_executor(conn.commit)
        except sqlite3.OperationalError as e:
            logger.warning(f"Transaction error on attempt {attempt + 1}: {e}")
            await self._run_in_executor(conn.rollback)
            await asyncio.sleep(0.1)
            await self.transaction(queries, attempt + 1)
        finally:
            await self._release_connection(conn)

    async def close_pool(self) -> None:
        while not self._connection_pool.empty():
            conn = await self._connection_pool.get()
            await self._run_in_executor(conn.close)
        self.executor.shutdown(wait=True)

    async def bulk_insert(self, table: str, columns: List[str], values: List[Tuple[Any, ...]]) -> None:
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        conn = await self._get_connection()
        try:
            await self._run_in_executor(conn.executemany, query, values)
            await self._run_in_executor(conn.commit)
        finally:
            await self._release_connection(conn)

    async def table_exists(self, table_name: str) -> bool:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = await self.fetchone(query, (table_name,))
        return result is not None

    async def create_table(self, table_name: str, columns: Dict[str, str]) -> None:
        columns_def = ', '.join([f"{col} {col_type}" for col, col_type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})"
        await self.execute(query)

    async def drop_table(self, table_name: str) -> None:
        query = f"DROP TABLE IF EXISTS {table_name}"
        await self.execute(query)

    async def clear_table(self, table_name: str) -> None:
        query = f"DELETE FROM {table_name}"
        await self.execute(query)
