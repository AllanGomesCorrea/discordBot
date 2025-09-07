import discord
from discord import app_commands
from datetime import datetime
from typing import List, Tuple
from services.expense_service import ExpenseService
from services.calculation_service import CalculationService
from repositories.sqlite_expense_repository import SQLiteExpenseRepository
from repositories.sqlite_split_repository import SQLiteSplitRepository
from config import DATABASE_PATH, MAX_MESSAGE_HISTORY

@app_commands.command(name="save_monthly", description="Salva o resumo mensal no banco de dados.")
async def save_monthly(interaction: discord.Interaction, month: int, year: int):
    """
    Salva o resumo mensal baseado nas mensagens do canal.
    
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
        # Buscar mensagens no canal
        channel = interaction.channel
        expenses_data = []
        
        async for message in channel.history(limit=MAX_MESSAGE_HISTORY):
            if message.content.startswith('-') and message.content.count(';') == 2:
                try:
                    value, description, person = [x.strip('- ').strip() for x in message.content.split(';')]
                    value = float(value.replace(',', '.'))
                    expenses_data.append((value, description, person))
                except Exception:
                    continue
        
        if not expenses_data:
            await interaction.followup.send("Nenhum gasto encontrado no padrão esperado (- Valor;Descrição;Pessoa)", ephemeral=True)
            return
        
        # Inicializar repositórios e serviço dentro da função
        expense_repo = SQLiteExpenseRepository(DATABASE_PATH)
        split_repo = SQLiteSplitRepository(DATABASE_PATH)
        expense_service = ExpenseService(expense_repo, split_repo)
        
        # Salvar no banco de dados
        await expense_service.save_monthly_data(expenses_data, month, year)
        
        # Usar o serviço de cálculos para feedback
        calculation = CalculationService.calculate_expenses(expenses_data)
        summary_text = CalculationService.format_summary_text(calculation, month, year, "Dados salvos para")
        
        await interaction.followup.send(summary_text, ephemeral=True)
        
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao salvar dados: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
