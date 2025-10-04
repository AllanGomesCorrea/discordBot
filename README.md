# Bot Discord - Gastos

Bot Discord para gerenciamento de gastos compartilhados com funcionalidades de cálculo de divisão de contas e persistência em banco de dados SQLite.

## Funcionalidades

### Comandos Básicos
- `/hello` - Comando de teste
- `/summary` - Mostra resumo das despesas do canal
- `/total_splited` - Calcula divisão de gastos e quem deve para quem

### Comandos de Música
- `/add_song` - Adiciona música à fila
- `/play_pause` - Reproduz/pausa música
- `/skip` - Pula música atual
- `/queue` - Mostra fila de músicas
- `/exit` - Sai do canal de voz

### Comandos de Persistência (NOVO)
- `/save_monthly <mês> <ano>` - Salva dados mensais no banco SQLite
- `/load_monthly <mês> <ano>` - Carrega dados salvos de um mês específico

## Arquitetura

O projeto segue os princípios SOLID e Clean Code:

### Estrutura de Pastas
```
├── commands/          # Comandos do Discord
├── models/           # Modelos de dados
├── repositories/     # Interfaces e implementações de repositório
├── services/         # Lógica de negócio
├── config.py         # Configurações centralizadas
├── main.py          # Ponto de entrada
└── requirements.txt  # Dependências
```

### Princípios SOLID Aplicados

1. **Single Responsibility Principle (SRP)**
   - Cada classe tem uma única responsabilidade
   - Repositórios apenas gerenciam dados
   - Serviços contêm lógica de negócio
   - Comandos apenas orquestram interações

2. **Open/Closed Principle (OCP)**
   - Interfaces de repositório permitem extensão
   - Novos tipos de repositório podem ser implementados

3. **Liskov Substitution Principle (LSP)**
   - Implementações de repositório são intercambiáveis
   - SQLiteExpenseRepository pode substituir ExpenseRepository

4. **Interface Segregation Principle (ISP)**
   - Interfaces específicas para cada tipo de repositório
   - Clientes não dependem de métodos não utilizados

5. **Dependency Inversion Principle (DIP)**
   - Serviços dependem de abstrações (interfaces)
   - Injeção de dependência nos construtores

## Banco de Dados

### Schema SQLite

#### Tabela `expenses`
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value REAL NOT NULL,
    description TEXT NOT NULL,
    paid_by TEXT NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela `splits`
```sql
CREATE TABLE splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debtor TEXT NOT NULL,
    creditor TEXT NOT NULL,
    amount REAL NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
BOT_TOKEN=seu_token_do_discord
DATABASE_PATH=expenses.db
LOG_LEVEL=INFO
MAX_MESSAGE_HISTORY=500
```

### Instalação
```bash
pip install -r requirements.txt
```

### Execução
```bash
python main.py
```

## Uso

### Formato de Mensagens
Para que o bot reconheça as despesas, use o formato:
```
- 25.50;Almoço;João
- 15.00;Uber;Maria
- 8.75;Café;Pedro
```

**✨ Suporte a Múltiplas Linhas:**
Agora você pode enviar várias despesas em uma única mensagem:
```
- 116,32;Internet Vencimento dia 10;Lan
- 274;Academia Vencimento dia 10 e 20;Lan
- 44,90;Netflix Vencimento dia 10;Lan
```

### Comandos Disponíveis

#### 📊 Resumo das Contas
```
/summary
```
**Novas funcionalidades:**
- ✅ **Detecção de erros**: Identifica mensagens fora do padrão e mostra quais são
- ✅ **Organização por pessoa**: Exibe despesas agrupadas por pessoa com totais individuais
- ✅ **Resumo estatístico**: Mostra total geral, número de pessoas e média por pessoa
- ✅ **Exportação Excel**: Botão para gerar arquivo .xlsx com todos os dados
- ✅ **Tratamento de mensagens longas**: Se o resumo for muito extenso, oferece download do Excel

#### 💾 Salvar Dados Mensais
```
/save_monthly 12 2024
```
- Analisa mensagens do canal
- Calcula divisão de gastos
- Salva no banco SQLite
- Sobrescreve dados existentes do mesmo mês/ano

#### 📂 Carregar Dados Salvos
```
/load_monthly 12 2024
```
- Carrega dados salvos do mês/ano especificado
- Mostra resumo completo com splits

#### 🧮 Cálculo de Divisão
```
/total_splited
```
- Mostra total por pessoa
- Calcula quem deve para quem
- Formato limpo e organizado

## Exemplo de Fluxo

1. Usuários enviam mensagens com gastos no canal
2. Comando `/save_monthly 12 2024` salva dados de dezembro/2024
3. Comando `/load_monthly 12 2024` recupera dados salvos
4. Dados persistem entre sessões do bot

## Tecnologias

- **Discord.py** - API do Discord
- **SQLite** - Banco de dados local
- **aiosqlite** - Interface assíncrona para SQLite
- **openpyxl** - Geração de planilhas Excel
- **python-dotenv** - Gerenciamento de variáveis de ambiente
