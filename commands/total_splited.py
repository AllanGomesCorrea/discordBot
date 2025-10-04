import discord
from discord import app_commands
from typing import List, Tuple
from config import MAX_MESSAGE_HISTORY
from services.calculation_service import CalculationService

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

@app_commands.command(name="total_splited", description="Mostra o total por pessoa e quem deve para quem.")
async def total_splited(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
        return
    
    try:
        channel = interaction.channel
        expenses_data = []
        
        async for message in channel.history(limit=MAX_MESSAGE_HISTORY):
            # Extrair despesas da mensagem (suporta múltiplas linhas)
            message_expenses = extract_expenses_from_message(message.content)
            expenses_data.extend(message_expenses)
        
        # Usar o serviço de cálculos
        calculation = CalculationService.calculate_expenses(expenses_data)
        
        if calculation.people_count == 0:
            await interaction.followup.send("Nenhum gasto encontrado no padrão esperado.", ephemeral=True)
            return
        
        # Formatar resultado usando o serviço
        result_text = CalculationService.format_totals_text(calculation)
        await interaction.followup.send(result_text, ephemeral=True)
        
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao processar comando: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
