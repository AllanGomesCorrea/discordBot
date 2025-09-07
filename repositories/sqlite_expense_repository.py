import sqlite3
import aiosqlite
from typing import List
from datetime import datetime
from models.expense import Expense
from .expense_repository import ExpenseRepository

class SQLiteExpenseRepository(ExpenseRepository):
    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
    
    async def _init_db(self) -> None:
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    value REAL NOT NULL,
                    description TEXT NOT NULL,
                    paid_by TEXT NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.commit()
    
    async def save_expenses(self, expenses: List[Expense]) -> None:
        if not expenses:
            return
        
        # Usar o primeiro expense para determinar mês/ano
        month, year = expenses[0].month, expenses[0].year
        
        async with aiosqlite.connect(self.db_path) as conn:
            await self._init_db()
            
            # Remover despesas existentes do mesmo mês/ano
            await conn.execute(
                'DELETE FROM expenses WHERE month = ? AND year = ?',
                (month, year)
            )
            
            # Inserir novas despesas
            for expense in expenses:
                await conn.execute('''
                    INSERT INTO expenses (value, description, paid_by, month, year, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    expense.value,
                    expense.description,
                    expense.paid_by,
                    expense.month,
                    expense.year,
                    expense.created_at
                ))
            
            await conn.commit()
    
    async def get_expenses_by_month(self, month: int, year: int) -> List[Expense]:
        async with aiosqlite.connect(self.db_path) as conn:
            await self._init_db()
            
            cursor = await conn.execute('''
                SELECT id, value, description, paid_by, month, year, created_at
                FROM expenses
                WHERE month = ? AND year = ?
                ORDER BY created_at
            ''', (month, year))
            
            rows = await cursor.fetchall()
            return [
                Expense(
                    id=row[0],
                    value=row[1],
                    description=row[2],
                    paid_by=row[3],
                    month=row[4],
                    year=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else None
                )
                for row in rows
            ]
    
    async def delete_expenses_by_month(self, month: int, year: int) -> None:
        async with aiosqlite.connect(self.db_path) as conn:
            await self._init_db()
            await conn.execute(
                'DELETE FROM expenses WHERE month = ? AND year = ?',
                (month, year)
            )
            await conn.commit()
