from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class ExpenseCalculation:
    """Resultado de cálculo de despesas"""
    total_by_person: Dict[str, float]
    total_sum: float
    people_count: int
    average: float
    balance_by_person: Dict[str, float]
    debtors: List[Tuple[str, float]]
    creditors: List[Tuple[str, float]]
    payments: List[Tuple[str, str, float]]  # (debtor, creditor, amount)

class CalculationService:
    """Serviço para cálculos de despesas e divisão de contas"""
    
    @staticmethod
    def calculate_expenses(expenses_data: List[Tuple[float, str, str]]) -> ExpenseCalculation:
        """
        Calcula totais, médias e divisão de despesas.
        
        Args:
            expenses_data: Lista de tuplas (valor, descrição, quem_pagou)
            
        Returns:
            ExpenseCalculation: Resultado completo dos cálculos
        """
        if not expenses_data:
            return ExpenseCalculation(
                total_by_person={},
                total_sum=0,
                people_count=0,
                average=0,
                balance_by_person={},
                debtors=[],
                creditors=[],
                payments=[]
            )
        
        # Calcular total por pessoa
        total_by_person = {}
        for value, _, person in expenses_data:
            total_by_person[person] = total_by_person.get(person, 0) + value
        
        people = list(total_by_person.keys())
        total_sum = sum(total_by_person.values())
        average = total_sum / len(people)
        
        # Calcular balanço por pessoa
        balance_by_person = {person: total_by_person[person] - average for person in people}
        
        # Separar devedores e credores
        debtors = [(person, -balance) for person, balance in balance_by_person.items() if balance < 0]
        creditors = [(person, balance) for person, balance in balance_by_person.items() if balance > 0]
        
        # Calcular pagamentos
        payments = []
        for debtor_name, amount_owed in debtors:
            for i, (creditor_name, amount_to_receive) in enumerate(creditors):
                if amount_owed == 0:
                    break
                payment_amount = min(amount_owed, amount_to_receive)
                if payment_amount > 0:
                    payments.append((debtor_name, creditor_name, payment_amount))
                    creditors[i] = (creditor_name, amount_to_receive - payment_amount)
                    amount_owed -= payment_amount
        
        return ExpenseCalculation(
            total_by_person=total_by_person,
            total_sum=total_sum,
            people_count=len(people),
            average=average,
            balance_by_person=balance_by_person,
            debtors=debtors,
            creditors=creditors,
            payments=payments
        )
    
    @staticmethod
    def format_summary_text(calculation: ExpenseCalculation, month: int, year: int, title: str) -> str:
        """
        Formata texto de resumo baseado nos cálculos.
        
        Args:
            calculation: Resultado dos cálculos
            month: Mês
            year: Ano
            title: Título do resumo
            
        Returns:
            str: Texto formatado
        """
        if calculation.people_count == 0:
            return "Nenhum gasto encontrado."
        
        summary_text = f"**{title} {month:02d}/{year}:**\n\n"
        summary_text += f"**Total de gastos:** R$ {calculation.total_sum:.2f}\n"
        summary_text += f"**Pessoas envolvidas:** {calculation.people_count}\n"
        summary_text += f"**Média por pessoa:** R$ {calculation.average:.2f}\n\n"
        
        summary_text += "**Gastos por pessoa:**\n"
        for person, total in sorted(calculation.total_by_person.items()):
            balance = calculation.balance_by_person[person]
            status = "recebe" if balance > 0 else "deve"
            summary_text += f"{person}: R$ {total:.2f} ({status} R$ {abs(balance):.2f})\n"
        
        if calculation.payments:
            summary_text += "\n**Quem deve para quem:**\n"
            for debtor, creditor, amount in calculation.payments:
                summary_text += f"{debtor} deve R$ {amount:.2f} para {creditor}\n"
        
        return summary_text
    
    @staticmethod
    def format_totals_text(calculation: ExpenseCalculation) -> str:
        """
        Formata texto de totais para o comando total_splited.
        
        Args:
            calculation: Resultado dos cálculos
            
        Returns:
            str: Texto formatado
        """
        if calculation.people_count == 0:
            return "Nenhum gasto encontrado."
        
        totals_text = "\n".join([
            f"{person}: R$ {total:.2f}" 
            for person, total in sorted(calculation.total_by_person.items())
        ])
        
        balances_text = "\n".join([
            f"{person}: {'recebe' if balance > 0 else 'deve'} R$ {abs(balance):.2f}" 
            for person, balance in sorted(calculation.balance_by_person.items())
        ])
        
        payments_text = "\n".join([
            f"{debtor} deve R$ {amount:.2f} para {creditor}"
            for debtor, creditor, amount in calculation.payments
        ]) if calculation.payments else "Todos estão quitados!"
        
        return (
            f"**Total por pessoa:**\n{totals_text}\n\n"
            f"**Balanços:**\n{balances_text}\n\n"
            f"**Quem deve para quem:**\n{payments_text}"
        )
