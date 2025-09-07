import sqlite3
import aiosqlite
from typing import List
from datetime import datetime
from models.split import Split
from .split_repository import SplitRepository

class SQLiteSplitRepository(SplitRepository):
    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
    
    async def _init_db(self) -> None:
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS splits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    debtor TEXT NOT NULL,
                    creditor TEXT NOT NULL,
                    amount REAL NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.commit()
    
    async def save_splits(self, splits: List[Split]) -> None:
        if not splits:
            return
        
        # Usar o primeiro split para determinar mês/ano
        month, year = splits[0].month, splits[0].year
        
        async with aiosqlite.connect(self.db_path) as conn:
            await self._init_db()
            
            # Remover splits existentes do mesmo mês/ano
            await conn.execute(
                'DELETE FROM splits WHERE month = ? AND year = ?',
                (month, year)
            )
            
            # Inserir novos splits
            for split in splits:
                await conn.execute('''
                    INSERT INTO splits (debtor, creditor, amount, month, year, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    split.debtor,
                    split.creditor,
                    split.amount,
                    split.month,
                    split.year,
                    split.created_at
                ))
            
            await conn.commit()
    
    async def get_splits_by_month(self, month: int, year: int) -> List[Split]:
        async with aiosqlite.connect(self.db_path) as conn:
            await self._init_db()
            
            cursor = await conn.execute('''
                SELECT id, debtor, creditor, amount, month, year, created_at
                FROM splits
                WHERE month = ? AND year = ?
                ORDER BY created_at
            ''', (month, year))
            
            rows = await cursor.fetchall()
            return [
                Split(
                    id=row[0],
                    debtor=row[1],
                    creditor=row[2],
                    amount=row[3],
                    month=row[4],
                    year=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None
                )
                for row in rows
            ]
    
    async def delete_splits_by_month(self, month: int, year: int) -> None:
        async with aiosqlite.connect(self.db_path) as conn:
            await self._init_db()
            await conn.execute(
                'DELETE FROM splits WHERE month = ? AND year = ?',
                (month, year)
            )
            await conn.commit()
