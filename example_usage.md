# Exemplo de Uso - Bot de Gastos Discord

## Cenário
Você e seus amigos fizeram várias despesas durante o mês de dezembro de 2024 e querem organizar e salvar os dados para consulta posterior.

## Passo 1: Enviar Mensagens de Gastos

### Formato Individual (mensagem por despesa):
```
- 25.50;Almoço no restaurante;João
- 15.00;Uber para o shopping;Maria
- 8.75;Café da manhã;Pedro
- 32.00;Ingressos do cinema;João
- 12.50;Lanche;Maria
- 18.25;Gasolina;Pedro
```

### ✨ Formato Múltiplas Linhas (várias despesas em uma mensagem):
```
- 116,32;Internet Vencimento dia 10;Lan
- 274;Academia Vencimento dia 10 e 20;Lan
- 44,90;Netflix Vencimento dia 10;Lan
```

## Passo 2: Verificar Resumo das Contas
Use o comando:
```
/summary
```

**O bot irá:**
- ✅ Analisar todas as mensagens do canal
- ✅ Detectar mensagens fora do padrão e mostrar quais são
- ✅ Organizar despesas por pessoa com totais individuais
- ✅ Mostrar resumo estatístico geral
- ✅ Oferecer opção de exportar para Excel

## Passo 3: Salvar Dados Mensais
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

## Passo 4: Consultar Dados Salvos
A qualquer momento, use:
```
/load_monthly 12 2024
```

O bot irá:
- Carregar dados salvos de dezembro/2024
- Mostrar resumo completo
- Exibir quem deve para quem

## Exemplo de Resposta do /summary

### Com mensagens inválidas detectadas:
```
⚠️ 2 linha(s) fora do padrão detectada(s):

**João** (15/12/2024 14:30):
  ❌ `- 25.50 Almoço João` (faltam pontos e vírgulas)
  ❌ `25.50;Almoço;` (pessoa em branco)

**Formato correto:** `- Valor;Descrição;Pessoa`

---
✅ **Resumo das Despesas:**

**João** (Total: R$ 57.50)
```
- R$ 25.50 | Almoço no restaurante
- R$ 32.00 | Ingressos do cinema
```

**Maria** (Total: R$ 27.50)
```
- R$ 15.00 | Uber para o shopping
- R$ 12.50 | Lanche
```

**Pedro** (Total: R$ 27.00)
```
- R$ 8.75 | Café da manhã
- R$ 18.25 | Gasolina
```

**📊 Resumo Geral:**
• Total de despesas: R$ 112.00
• Pessoas envolvidas: 3
• Média por pessoa: R$ 37.33

Deseja gerar um arquivo .xlsx com o resultado?
```

## Vantagens
- ✅ Dados persistem entre sessões do bot
- ✅ Sobrescreve dados antigos do mesmo mês
- ✅ Cálculo automático de divisão
- ✅ Histórico completo de gastos
- ✅ Interface limpa e organizada
