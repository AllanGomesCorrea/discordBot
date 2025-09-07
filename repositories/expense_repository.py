from abc import ABC, abstractmethod
from typing import List, Optional
from models.expense import Expense

class ExpenseRepository(ABC):
    @abstractmethod
    async def save_expenses(self, expenses: List[Expense]) -> None:
        """Salva uma lista de despesas, sobrescrevendo as existentes do mesmo mês/ano"""
        pass
    
    @abstractmethod
    async def get_expenses_by_month(self, month: int, year: int) -> List[Expense]:
        """Busca despesas por mês e ano"""
        pass
    
    @abstractmethod
    async def delete_expenses_by_month(self, month: int, year: int) -> None:
        """Remove todas as despesas de um mês/ano específico"""
        pass
