# Exemplo de Uso - Comandos de Persistência

## Cenário
Você e seus amigos fizeram várias despesas durante o mês de dezembro de 2024 e querem salvar os dados para consulta posterior.

## Passo 1: Enviar Mensagens de Gastos
No canal do Discord, envie mensagens no formato:
```
- 25.50;Almoço no restaurante;João
- 15.00;Uber para o shopping;Maria
- 8.75;Café da manhã;Pedro
- 32.00;Ingressos do cinema;João
- 12.50;Lanche;Maria
- 18.25;Gasolina;Pedro
```

## Passo 2: Salvar Dados Mensais
Use o comando:
```
/save_monthly 12 2024
```

O bot irá:
- Analisar todas as mensagens do canal
- Calcular o total por pessoa
- Calcular quem deve para quem
- Salvar tudo no banco SQLite
- Mostrar um resumo dos dados salvos

## Passo 3: Consultar Dados Salvos
A qualquer momento, use:
```
/load_monthly 12 2024
```

O bot irá:
- Carregar dados salvos de dezembro/2024
- Mostrar resumo completo
- Exibir quem deve para quem

## Exemplo de Resposta
```
**Dados salvos para 12/2024:**

**Total de gastos:** R$ 111.00
**Pessoas envolvidas:** 3
**Média por pessoa:** R$ 37.00

**Gastos por pessoa:**
João: R$ 57.50 (deve R$ 20.50)
Maria: R$ 27.50 (recebe R$ 9.50)
Pedro: R$ 27.00 (recebe R$ 10.00)

**Quem deve para quem:**
João deve R$ 9.50 para Maria
João deve R$ 10.00 para Pedro
```

## Vantagens
- ✅ Dados persistem entre sessões do bot
- ✅ Sobrescreve dados antigos do mesmo mês
- ✅ Cálculo automático de divisão
- ✅ Histórico completo de gastos
- ✅ Interface limpa e organizada
