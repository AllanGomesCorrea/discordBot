from typing import List, Dict, Tuple
from datetime import datetime
from models.expense import Expense
from models.split import Split
from repositories.expense_repository import ExpenseRepository
from repositories.split_repository import SplitRepository
from services.calculation_service import CalculationService

class ExpenseService:
    def __init__(self, expense_repository: ExpenseRepository, split_repository: SplitRepository):
        self.expense_repository = expense_repository
        self.split_repository = split_repository
    
    async def save_monthly_data(self, expenses_data: List[Tuple[float, str, str]], month: int, year: int) -> None:
        """
        Salva dados mensais de despesas e calcula/armazena os splits correspondentes.
        
        Args:
            expenses_data: Lista de tuplas (valor, descrição, quem_pagou)
            month: Mês (1-12)
            year: Ano
        """
        # Converter dados para objetos Expense
        expenses = [
            Expense(
                id=None,
                value=value,
                description=description,
                paid_by=paid_by,
                month=month,
                year=year
            )
            for value, description, paid_by in expenses_data
        ]
        
        # Salvar despesas
        await self.expense_repository.save_expenses(expenses)
        
        # Calcular e salvar splits usando o CalculationService
        splits = self._calculate_splits(expenses_data, month, year)
        await self.split_repository.save_splits(splits)
    
    def _calculate_splits(self, expenses_data: List[Tuple[float, str, str]], month: int, year: int) -> List[Split]:
        """
        Calcula quem deve para quem baseado nas despesas usando o CalculationService.
        """
        # Usar o CalculationService para obter os cálculos
        calculation = CalculationService.calculate_expenses(expenses_data)
        
        # Converter payments para objetos Split
        splits = []
        for debtor, creditor, amount in calculation.payments:
            splits.append(Split(
                id=None,
                debtor=debtor,
                creditor=creditor,
                amount=amount,
                month=month,
                year=year
            ))
        
        return splits
    
    async def get_monthly_summary(self, month: int, year: int) -> Dict:
        """
        Retorna resumo mensal com despesas e splits.
        """
        expenses = await self.expense_repository.get_expenses_by_month(month, year)
        splits = await self.split_repository.get_splits_by_month(month, year)
        
        return {
            'expenses': expenses,
            'splits': splits,
            'month': month,
            'year': year
        }
    
    async def get_expenses_by_month(self, month: int, year: int) -> List[Expense]:
        """Retorna despesas de um mês específico."""
        return await self.expense_repository.get_expenses_by_month(month, year)
    
    async def get_splits_by_month(self, month: int, year: int) -> List[Split]:
        """Retorna splits de um mês específico."""
        return await self.split_repository.get_splits_by_month(month, year)
