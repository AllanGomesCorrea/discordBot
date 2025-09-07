import discord
from discord import app_commands
from datetime import datetime
from typing import List, Tuple
from services.expense_service import ExpenseService
from repositories.sqlite_expense_repository import SQLiteExpenseRepository
from repositories.sqlite_split_repository import SQLiteSplitRepository
from config import DATABASE_PATH

# Inicializar repositórios e serviço
expense_repo = SQLiteExpenseRepository(DATABASE_PATH)
split_repo = SQLiteSplitRepository(DATABASE_PATH)
expense_service = ExpenseService(expense_repo, split_repo)

@app_commands.command(name="load_monthly", description="Carrega dados salvos de um mês específico.")
async def load_monthly(interaction: discord.Interaction, month: int, year: int):
    """
    Carrega dados salvos de um mês específico.
    
    Args:
        month: Mês (1-12)
        year: Ano (ex: 2024)
    """
    if not (1 <= month <= 12):
        await interaction.response.send_message("Mês deve estar entre 1 e 12.", ephemeral=True)
        return
    
    if year < 2000 or year > 2100:
        await interaction.response.send_message("Ano deve estar entre 2000 e 2100.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
        return
    
    try:
        summary = await expense_service.get_monthly_summary(month, year)
        
        if not summary['expenses']:
            await interaction.followup.send(f"Nenhum dado encontrado para {month:02d}/{year}.", ephemeral=True)
            return
        
        # Calcular estatísticas
        total_by_person = {}
        for expense in summary['expenses']:
            total_by_person[expense.paid_by] = total_by_person.get(expense.paid_by, 0) + expense.value
        
        total_sum = sum(total_by_person.values())
        people_count = len(total_by_person)
        average = total_sum / people_count
        
        # Gerar mensagem
        summary_text = f"**Dados carregados de {month:02d}/{year}:**\n\n"
        summary_text += f"**Total de gastos:** R$ {total_sum:.2f}\n"
        summary_text += f"**Pessoas envolvidas:** {people_count}\n"
        summary_text += f"**Média por pessoa:** R$ {average:.2f}\n\n"
        
        summary_text += "**Gastos por pessoa:**\n"
        for person, total in sorted(total_by_person.items()):
            balance = total - average
            status = "recebe" if balance > 0 else "deve"
            summary_text += f"{person}: R$ {total:.2f} ({status} R$ {abs(balance):.2f})\n"
        
        if summary['splits']:
            summary_text += "\n**Quem deve para quem:**\n"
            for split in summary['splits']:
                summary_text += f"{split.debtor} deve R$ {split.amount:.2f} para {split.creditor}\n"
        
        await interaction.followup.send(summary_text, ephemeral=True)
        
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao carregar dados: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
