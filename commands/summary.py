import discord
from discord import app_commands
from discord.ui import View, Button
import openpyxl
from io import BytesIO
from config import MAX_MESSAGE_HISTORY
from services.excel_service import ExcelService
from typing import Dict, List, Tuple, Optional
from datetime import datetime

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

def analyze_message_content(message_content: str) -> Tuple[List[Tuple[float, str, str]], List[str]]:
    """
    Analisa o conteúdo de uma mensagem e retorna despesas válidas e linhas inválidas.
    
    Args:
        message_content: Conteúdo da mensagem
        
    Returns:
        Tupla (despesas_válidas, linhas_inválidas)
    """
    valid_expenses = []
    invalid_lines = []
    lines = message_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:  # Linha vazia
            continue
            
        expense = parse_expense_line(line)
        if expense:
            valid_expenses.append(expense)
        else:
            # Verifica se a linha parece ser uma tentativa de despesa
            if line.startswith('-') or ';' in line:
                invalid_lines.append(line)
    
    return valid_expenses, invalid_lines

def format_summary_by_person(expenses_by_person: Dict[str, List[Tuple[float, str, str]]]) -> str:
    """
    Formata o resumo organizando por pessoa com totais.
    
    Args:
        expenses_by_person: Dicionário com pessoa como chave e lista de despesas como valor
        
    Returns:
        Texto formatado do resumo
    """
    result_lines = []
    
    for person in sorted(expenses_by_person.keys()):
        expenses = expenses_by_person[person]
        total = sum(expense[0] for expense in expenses)
        
        result_lines.append(f"**{person}** (Total: R$ {total:.2f})")
        result_lines.append("```")
        
        for value, description, _ in expenses:
            result_lines.append(f"- R$ {value:.2f} | {description}")
        
        result_lines.append("```")
        result_lines.append("")  # Linha em branco entre pessoas
    
    return "\n".join(result_lines)

class ExcelExportView(View):
    def __init__(self, expenses_by_person: Dict[str, List[Tuple[float, str, str]]]):
        super().__init__(timeout=300)
        self.expenses_by_person = expenses_by_person

    @discord.ui.button(label="Gerar .xlsx", style=discord.ButtonStyle.primary)
    async def generate_xlsx(self, interaction: discord.Interaction, button: Button):
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Converter para formato esperado pelo ExcelService
            excel_data = {}
            for person, expenses in self.expenses_by_person.items():
                excel_data[person] = [f"- {value};{description};{person}" for value, description, _ in expenses]
            
            # Gerar arquivo Excel
            excel_service = ExcelService()
            file_path = excel_service.generate_expenses_excel(excel_data)
            
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

@app_commands.command(name="summary", description="Mostra o resultado das contas organizado por pessoa.")
async def summary(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
        return
    
    try:
        channel = interaction.channel
        expenses_by_person = {}
        invalid_messages = []
        total_invalid_lines = 0
        
        async for message in channel.history(limit=MAX_MESSAGE_HISTORY):
            # Analisar mensagem para despesas válidas e inválidas
            valid_expenses, invalid_lines = analyze_message_content(message.content)
            
            # Processar despesas válidas
            for value, description, person in valid_expenses:
                if person not in expenses_by_person:
                    expenses_by_person[person] = []
                expenses_by_person[person].append((value, description, person))
            
            # Coletar mensagens com linhas inválidas
            if invalid_lines:
                total_invalid_lines += len(invalid_lines)
                message_info = {
                    'author': message.author.display_name,
                    'timestamp': message.created_at.strftime("%d/%m/%Y %H:%M"),
                    'invalid_lines': invalid_lines
                }
                invalid_messages.append(message_info)
        
        # Construir mensagem de resposta
        response_parts = []
        
        # Cabeçalho com informações sobre mensagens inválidas
        if invalid_messages:
            response_parts.append(f"⚠️ **{total_invalid_lines} linha(s) fora do padrão detectada(s):**")
            response_parts.append("")
            
            for msg_info in invalid_messages[:5]:  # Limitar a 5 mensagens para não ficar muito longo
                response_parts.append(f"**{msg_info['author']}** ({msg_info['timestamp']}):")
                for line in msg_info['invalid_lines']:
                    response_parts.append(f"  ❌ `{line}`")
                response_parts.append("")
            
            if len(invalid_messages) > 5:
                response_parts.append(f"... e mais {len(invalid_messages) - 5} mensagem(ns) com problemas.")
                response_parts.append("")
            
            response_parts.append("**Formato correto:** `- Valor;Descrição;Pessoa`")
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("")
        
        if not expenses_by_person:
            if invalid_messages:
                response_parts.append("❌ Nenhuma despesa válida encontrada.")
            else:
                response_parts.append("❌ Nenhuma mensagem no padrão esperado encontrada.")
                response_parts.append("**Formato:** `- Valor;Descrição;Pessoa`")
            
            await interaction.followup.send("\n".join(response_parts), ephemeral=True)
            return
        
        # Adicionar resumo das despesas válidas
        response_parts.append("✅ **Resumo das Despesas:**")
        response_parts.append("")
        
        # Formatar resumo por pessoa
        summary_text = format_summary_by_person(expenses_by_person)
        response_parts.append(summary_text)
        
        # Calcular totais gerais
        total_expenses = sum(sum(expense[0] for expense in expenses) for expenses in expenses_by_person.values())
        total_people = len(expenses_by_person)
        average_per_person = total_expenses / total_people if total_people > 0 else 0
        
        response_parts.append("**📊 Resumo Geral:**")
        response_parts.append(f"• Total de despesas: R$ {total_expenses:.2f}")
        response_parts.append(f"• Pessoas envolvidas: {total_people}")
        response_parts.append(f"• Média por pessoa: R$ {average_per_person:.2f}")
        
        # Verificar se a mensagem é muito longa
        full_response = "\n".join(response_parts)
        
        if len(full_response) > 1900:
            # Se for muito longa, dividir em partes
            await interaction.followup.send(
                "📋 **Resumo muito extenso!** Use o botão abaixo para gerar um arquivo Excel com todos os detalhes.",
                ephemeral=True,
                view=ExcelExportView(expenses_by_person)
            )
        else:
            # Adicionar botão para gerar Excel
            response_parts.append("")
            response_parts.append("Deseja gerar um arquivo .xlsx com o resultado?")
            
            await interaction.followup.send(
                "\n".join(response_parts),
                ephemeral=True,
                view=ExcelExportView(expenses_by_person)
            )
        
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao processar comando: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
