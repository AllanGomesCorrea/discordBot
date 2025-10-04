import discord
from discord import app_commands
from datetime import datetime
from typing import List, Tuple
from services.expense_service import ExpenseService
from services.calculation_service import CalculationService
from repositories.sqlite_expense_repository import SQLiteExpenseRepository
from repositories.sqlite_split_repository import SQLiteSplitRepository
from config import DATABASE_PATH, MAX_MESSAGE_HISTORY

def parse_expense_line(line: str) -> Tuple[float, str, str] | None:
    """
    Parse uma linha de despesa no formato: - Valor;Descrição;Pessoa
    
    Args:
        line: Linha de texto a ser parseada
        
    Returns:
        Tupla (valor, descrição, pessoa) ou None se inválida
    """
    line = line.strip()
    if not line.startswith('-'):
        return None
    
    # Remove o '-' inicial e divide por ';'
    parts = line[1:].split(';')
    if len(parts) != 3:
        return None
    
    try:
        value_str, description, person = [part.strip() for part in parts]
        value = float(value_str.replace(',', '.'))
        return (value, description, person)
    except (ValueError, IndexError):
        return None

def extract_expenses_from_message(message_content: str) -> List[Tuple[float, str, str]]:
    """
    Extrai despesas de uma mensagem, suportando tanto formato individual quanto múltiplas linhas.
    
    Args:
        message_content: Conteúdo da mensagem
        
    Returns:
        Lista de tuplas (valor, descrição, pessoa)
    """
    expenses = []
    lines = message_content.split('\n')
    
    for line in lines:
        expense = parse_expense_line(line)
        if expense:
            expenses.append(expense)
    
    return expenses

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
            # Extrair despesas da mensagem (suporta múltiplas linhas)
            message_expenses = extract_expenses_from_message(message.content)
            expenses_data.extend(message_expenses)
        
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
