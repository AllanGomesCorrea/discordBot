import discord
from discord import app_commands
from discord.ui import View, Button
import openpyxl
from io import BytesIO
from config import MAX_MESSAGE_HISTORY
from services.excel_service import ExcelService
from typing import Dict, List, Tuple

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

class ExcelExportView(View):
    def __init__(self, expenses_by_person: Dict[str, List[str]]):
        super().__init__(timeout=300)
        self.expenses_by_person = expenses_by_person

    @discord.ui.button(label="Gerar .xlsx", style=discord.ButtonStyle.primary)
    async def generate_xlsx(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Gerar arquivo Excel
            excel_service = ExcelService()
            file_path = excel_service.generate_expenses_excel(self.expenses_by_person)
            
            # Enviar arquivo
            with open(file_path, 'rb') as f:
                file = discord.File(f, filename="gastos.xlsx")
                await interaction.followup.send("Arquivo Excel gerado com sucesso!", file=file, ephemeral=True)
            
            # Limpar arquivo temporário
            import os
            os.remove(file_path)
            
        except Exception as e:
            try:
                await interaction.followup.send(f"Erro ao gerar Excel: {str(e)}", ephemeral=True)
            except discord.NotFound:
                pass

@app_commands.command(name="summary", description="Mostra o resultado das contas.")
async def summary(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
        return
    
    try:
        channel = interaction.channel
        expenses_by_person = {}
        
        async for message in channel.history(limit=MAX_MESSAGE_HISTORY):
            # Extrair despesas da mensagem (suporta múltiplas linhas)
            message_expenses = extract_expenses_from_message(message.content)
            
            for value, description, person in message_expenses:
                if person not in expenses_by_person:
                    expenses_by_person[person] = []
                expenses_by_person[person].append(f"- {value};{description};{person}")
        
        if not expenses_by_person:
            await interaction.followup.send("Sem mensagens no padrão esperado (- Valor;Descrição;Pessoa)", ephemeral=True)
            return
        
        result_lines = []
        for person in sorted(expenses_by_person.keys()):
            result_lines.extend(expenses_by_person[person])
        result_text = "\n".join(result_lines)
        
        if len(result_text) > 1900:
            await interaction.followup.send("Muitas mensagens! Resultado é muito grande para exibir aqui.", ephemeral=True)
        else:
            view = ExcelExportView(expenses_by_person)
            await interaction.followup.send(
                f"**Resultado:**\n{result_text}\n\nDeseja gerar um arquivo .xlsx com o resultado?",
                ephemeral=True,
                view=view
            )
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao processar comando: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
