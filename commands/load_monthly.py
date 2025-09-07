import discord
from discord import app_commands
from datetime import datetime
from typing import List, Tuple
from services.expense_service import ExpenseService
from services.calculation_service import CalculationService
from repositories.sqlite_expense_repository import SQLiteExpenseRepository
from repositories.sqlite_split_repository import SQLiteSplitRepository
from config import DATABASE_PATH

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
        # Inicializar repositórios e serviço dentro da função
        expense_repo = SQLiteExpenseRepository(DATABASE_PATH)
        split_repo = SQLiteSplitRepository(DATABASE_PATH)
        expense_service = ExpenseService(expense_repo, split_repo)
        
        summary = await expense_service.get_monthly_summary(month, year)
        
        if not summary['expenses']:
            await interaction.followup.send(f"Nenhum dado encontrado para {month:02d}/{year}.", ephemeral=True)
            return
        
        # Converter expenses para formato do CalculationService
        expenses_data = [
            (expense.value, expense.description, expense.paid_by)
            for expense in summary['expenses']
        ]
        
        # Usar o serviço de cálculos
        calculation = CalculationService.calculate_expenses(expenses_data)
        summary_text = CalculationService.format_summary_text(calculation, month, year, "Dados carregados de")
        
        await interaction.followup.send(summary_text, ephemeral=True)
        
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao carregar dados: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
