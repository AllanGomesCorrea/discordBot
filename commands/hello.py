import discord
from discord import app_commands

@app_commands.command(name="hello", description="Boas vindas")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Olá, {interaction.user.name}! Tudo bem?", ephemeral=True) 