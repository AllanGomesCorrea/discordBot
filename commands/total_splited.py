import discord
from discord import app_commands
from config import MAX_MESSAGE_HISTORY
from services.calculation_service import CalculationService

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
            if message.content.startswith('-') and message.content.count(';') == 2:
                try:
                    value, description, person = [x.strip('- ').strip() for x in message.content.split(';')]
                    value = float(value.replace(',', '.'))
                    expenses_data.append((value, description, person))
                except Exception:
                    continue
        
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
