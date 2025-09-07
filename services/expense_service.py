from typing import List, Dict, Tuple
from datetime import datetime
from models.expense import Expense
from models.split import Split
from repositories.expense_repository import ExpenseRepository
from repositories.split_repository import SplitRepository

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
        
        # Calcular e salvar splits
        splits = self._calculate_splits(expenses_data, month, year)
        await self.split_repository.save_splits(splits)
    
    def _calculate_splits(self, expenses_data: List[Tuple[float, str, str]], month: int, year: int) -> List[Split]:
        """
        Calcula quem deve para quem baseado nas despesas.
        """
        # Calcular total por pessoa
        total_by_person = {}
        for value, _, paid_by in expenses_data:
            total_by_person[paid_by] = total_by_person.get(paid_by, 0) + value
        
        people = list(total_by_person.keys())
        total_sum = sum(total_by_person.values())
        average_expense = total_sum / len(people)
        
        # Calcular balanço por pessoa
        balance_by_person = {person: total_by_person[person] - average_expense for person in people}
        
        # Separar devedores e credores
        debtors = [(person, -balance) for person, balance in balance_by_person.items() if balance < 0]
        creditors = [(person, balance) for person, balance in balance_by_person.items() if balance > 0]
        
        # Calcular pagamentos
        splits = []
        for debtor_name, amount_owed in debtors:
            for i, (creditor_name, amount_to_receive) in enumerate(creditors):
                if amount_owed == 0:
                    break
                payment_amount = min(amount_owed, amount_to_receive)
                if payment_amount > 0:
                    splits.append(Split(
                        id=None,
                        debtor=debtor_name,
                        creditor=creditor_name,
                        amount=payment_amount,
                        month=month,
                        year=year
                    ))
                    creditors[i] = (creditor_name, amount_to_receive - payment_amount)
                    amount_owed -= payment_amount
        
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
