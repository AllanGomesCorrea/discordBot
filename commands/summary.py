import discord
from discord import app_commands
from discord.ui import View, Button
import openpyxl
from io import BytesIO

class ExcelExportView(View):
    def __init__(self, expenses_by_person):
        super().__init__(timeout=60)
        self.expenses_by_person = expenses_by_person

    @discord.ui.button(label="Gerar .xlsx", style=discord.ButtonStyle.primary)
    async def generate_xlsx(self, interaction: discord.Interaction, button: Button):
        all_expenses = []
        for person, expenses in self.expenses_by_person.items():
            for expense in expenses:
                value, description, person_name = expense.lstrip('- ').split(';')
                all_expenses.append((value.strip(), description.strip(), person_name.strip()))
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Valor", "Descrição", "Pessoa"])
        for value, description, person_name in all_expenses:
            ws.append([value, description, person_name])
        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        await interaction.response.send_message(
            "Aqui está o arquivo .xlsx com o resultado:",
            file=discord.File(fp=file_stream, filename="resultado.xlsx"),
            ephemeral=True
        )
        self.stop()

@app_commands.command(name="summary", description="Mostra o resultado das contas.")
async def summary(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    channel = interaction.channel
    expenses_by_person = {}
    async for message in channel.history(limit=500):
        if message.content.startswith('-') and message.content.count(';') == 2:
            try:
                value, description, person = [x.strip('- ').strip() for x in message.content.split(';')]
                if person not in expenses_by_person:
                    expenses_by_person[person] = []
                expenses_by_person[person].append(f"- {value};{description};{person}")
            except Exception:
                continue
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