import discord
from discord import app_commands
from config import MAX_MESSAGE_HISTORY

@app_commands.command(name="total_splited", description="Mostra o total por pessoa e quem deve para quem.")
async def total_splited(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
        # Interação já expirou, não podemos responder
        return
    
    try:
        channel = interaction.channel
        expenses = []
        async for message in channel.history(limit=MAX_MESSAGE_HISTORY):
            if message.content.startswith('-') and message.content.count(';') == 2:
                try:
                    value, description, person = [x.strip('- ').strip() for x in message.content.split(';')]
                    value = float(value.replace(',', '.'))
                    expenses.append((person, value))
                except Exception:
                    continue
        
        if not expenses:
            await interaction.followup.send("Nenhum gasto encontrado no padrão esperado.", ephemeral=True)
            return
        
        total_by_person = {}
        for person, value in expenses:
            total_by_person[person] = total_by_person.get(person, 0) + value
        
        people = list(total_by_person.keys())
        total_sum = sum(total_by_person.values())
        average_expense = total_sum / len(people)
        balance_by_person = {person: total_by_person[person] - average_expense for person in people}
        
        totals_text = "\n".join([f"{person}: R$ {total_by_person[person]:.2f}" for person in people])
        balances_text = "\n".join([f"{person}: {'recebe' if balance > 0 else 'deve'} R$ {abs(balance):.2f}" for person, balance in balance_by_person.items()])
        
        debtors = [(person, -balance) for person, balance in balance_by_person.items() if balance < 0]
        creditors = [(person, balance) for person, balance in balance_by_person.items() if balance > 0]
        payments = []
        
        for debtor_name, amount_owed in debtors:
            for i, (creditor_name, amount_to_receive) in enumerate(creditors):
                if amount_owed == 0:
                    break
                payment_amount = min(amount_owed, amount_to_receive)
                if payment_amount > 0:
                    payments.append(f"{debtor_name} deve R$ {payment_amount:.2f} para {creditor_name}")
                    creditors[i] = (creditor_name, amount_to_receive - payment_amount)
                    amount_owed -= payment_amount
        
        payments_text = "\n".join(payments) if payments else "Todos estão quitados!"
        
        final_text = (
            f"**Total por pessoa:**\n{totals_text}\n\n"
            f"**Balanços:**\n{balances_text}\n\n"
            f"**Quem deve para quem:**\n{payments_text}"
        )
        
        await interaction.followup.send(final_text, ephemeral=True)
        
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro ao processar comando: {str(e)}", ephemeral=True)
        except discord.NotFound:
            # Interação expirou, não podemos responder
            pass
