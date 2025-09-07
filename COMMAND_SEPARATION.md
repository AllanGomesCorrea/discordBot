# Separação de Comandos

## Princípio Aplicado

Cada comando Discord deve estar em seu próprio arquivo, seguindo o princípio de **Single Responsibility Principle (SRP)** do SOLID.

## Estrutura Atual

```
commands/
├── __init__.py          # Registro de todos os comandos
├── hello.py             # Comando /hello
├── summary.py           # Comando /summary
├── total_splited.py     # Comando /total_splited
├── save_monthly.py      # Comando /save_monthly
├── load_monthly.py      # Comando /load_monthly
└── play_song.py         # Comandos de música (/add_song, /play_pause, etc.)
```

## Vantagens da Separação

### 1. **Manutenibilidade**
- Cada comando é independente
- Fácil localização de funcionalidades
- Modificações isoladas

### 2. **Testabilidade**
- Comandos podem ser testados individualmente
- Mock de dependências mais fácil
- Testes unitários específicos

### 3. **Reutilização**
- Comandos podem ser reutilizados
- Lógica compartilhada em services
- Importação seletiva

### 4. **Organização**
- Código mais limpo e organizado
- Responsabilidades claras
- Fácil navegação

## Padrão de Arquivo

Cada arquivo de comando segue o padrão:

```python
import discord
from discord import app_commands
# ... outras importações específicas

# Inicialização de dependências (se necessário)
# service = SomeService()

@app_commands.command(name="command_name", description="Descrição do comando.")
async def command_name(interaction: discord.Interaction, param1: int, param2: str):
    """
    Docstring do comando.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
    """
    # Validação de parâmetros
    if not (1 <= param1 <= 12):
        await interaction.response.send_message("Erro de validação.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
        return
    
    try:
        # Lógica do comando
        result = await some_service.process_data(param1, param2)
        await interaction.followup.send(result, ephemeral=True)
    except Exception as e:
        try:
            await interaction.followup.send(f"Erro: {str(e)}", ephemeral=True)
        except discord.NotFound:
            pass
```

## Registro de Comandos

Todos os comandos são registrados no `__init__.py`:

```python
from .save_monthly import save_monthly
from .load_monthly import load_monthly

def register_commands(bot):
    bot.tree.add_command(save_monthly)
    bot.tree.add_command(load_monthly)
```

## Comandos Agrupados

Alguns comandos relacionados podem ficar no mesmo arquivo:

- **`play_song.py`**: Contém todos os comandos de música
  - `/add_song`
  - `/play_pause`
  - `/skip`
  - `/queue`
  - `/exit`

## Boas Práticas

### ✅ **Fazer:**
- Um comando por arquivo (quando possível)
- Validação de parâmetros no início
- Tratamento de erros robusto
- Documentação clara
- Importações específicas

### ❌ **Evitar:**
- Múltiplos comandos não relacionados no mesmo arquivo
- Lógica de negócio nos comandos
- Tratamento de erros inadequado
- Importações desnecessárias

## Exemplo de Refatoração

### Antes (❌):
```python
# commands/save_monthly.py
@app_commands.command(name="save_monthly", ...)
async def save_monthly(...):
    # lógica do save

@app_commands.command(name="load_monthly", ...)
async def load_monthly(...):
    # lógica do load
```

### Depois (✅):
```python
# commands/save_monthly.py
@app_commands.command(name="save_monthly", ...)
async def save_monthly(...):
    # lógica do save

# commands/load_monthly.py
@app_commands.command(name="load_monthly", ...)
async def load_monthly(...):
    # lógica do load
```

## Benefícios da Refatoração

1. **Separação clara** de responsabilidades
2. **Manutenção mais fácil** de cada comando
3. **Testes independentes** para cada funcionalidade
4. **Reutilização** de código comum
5. **Organização** melhor do projeto

## Status

✅ **Comandos separados corretamente**
✅ **Padrão consistente aplicado**
✅ **Registro atualizado**
✅ **Compilação sem erros**
