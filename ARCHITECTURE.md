# Arquitetura do Sistema

## Visão Geral
O sistema foi implementado seguindo os princípios SOLID e Clean Code, com separação clara de responsabilidades e injeção de dependências.

## Diagrama de Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │   Commands      │    │   Services      │
│                 │    │                 │    │                 │
│  main.py        │───▶│ save_monthly    │───▶│ ExpenseService  │
│                 │    │ load_monthly    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Models        │    │  Repositories   │    │   Database      │
│                 │    │                 │    │                 │
│ Expense         │◀───│ ExpenseRepo     │───▶│ SQLite          │
│ Split           │    │ SplitRepo       │    │ expenses.db     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Camadas da Aplicação

### 1. Camada de Apresentação (Commands)
- **Responsabilidade**: Interação com usuários do Discord
- **Arquivos**: `commands/save_monthly.py`
- **Princípios**: SRP - apenas orquestração de comandos

### 2. Camada de Serviços
- **Responsabilidade**: Lógica de negócio
- **Arquivos**: `services/expense_service.py`
- **Princípios**: SRP - apenas lógica de negócio

### 3. Camada de Repositório
- **Responsabilidade**: Acesso a dados
- **Arquivos**: 
  - `repositories/expense_repository.py` (interface)
  - `repositories/sqlite_expense_repository.py` (implementação)
  - `repositories/split_repository.py` (interface)
  - `repositories/sqlite_split_repository.py` (implementação)
- **Princípios**: DIP - dependência de abstrações

### 4. Camada de Modelos
- **Responsabilidade**: Representação de dados
- **Arquivos**: `models/expense.py`, `models/split.py`
- **Princípios**: SRP - apenas estrutura de dados

## Princípios SOLID Aplicados

### Single Responsibility Principle (SRP)
- ✅ Cada classe tem uma única responsabilidade
- ✅ Commands apenas orquestram
- ✅ Services apenas contêm lógica de negócio
- ✅ Repositories apenas gerenciam dados

### Open/Closed Principle (OCP)
- ✅ Interfaces de repositório permitem extensão
- ✅ Novos tipos de repositório podem ser implementados sem modificar código existente

### Liskov Substitution Principle (LSP)
- ✅ SQLiteExpenseRepository pode substituir ExpenseRepository
- ✅ SQLiteSplitRepository pode substituir SplitRepository

### Interface Segregation Principle (ISP)
- ✅ Interfaces específicas para cada tipo de repositório
- ✅ Clientes não dependem de métodos não utilizados

### Dependency Inversion Principle (DIP)
- ✅ ExpenseService depende de abstrações (interfaces)
- ✅ Injeção de dependência nos construtores
- ✅ Alto nível não depende de baixo nível

## Fluxo de Dados

### Salvar Dados Mensais
1. **Command** recebe interação do Discord
2. **Command** extrai dados das mensagens do canal
3. **Command** chama **Service** com dados extraídos
4. **Service** converte dados para **Models**
5. **Service** chama **Repository** para salvar
6. **Repository** persiste no **Database**
7. **Service** calcula splits e salva via **Repository**
8. **Command** retorna feedback ao usuário

### Carregar Dados Mensais
1. **Command** recebe parâmetros do usuário
2. **Command** chama **Service** com mês/ano
3. **Service** chama **Repository** para buscar dados
4. **Repository** consulta **Database**
5. **Service** processa e formata dados
6. **Command** retorna resultado ao usuário

## Vantagens da Arquitetura

### Manutenibilidade
- Código organizado em camadas bem definidas
- Responsabilidades claras e separadas
- Fácil localização de funcionalidades

### Testabilidade
- Interfaces permitem mock de dependências
- Lógica de negócio isolada em services
- Repositórios podem ser testados independentemente

### Extensibilidade
- Novos tipos de repositório podem ser adicionados
- Novos comandos podem reutilizar services existentes
- Fácil adição de novos modelos de dados

### Flexibilidade
- Troca de banco de dados sem afetar lógica de negócio
- Configuração centralizada
- Injeção de dependências permite diferentes implementações

## Configuração e Inicialização

### Configuração Centralizada
- `config.py` centraliza todas as configurações
- Variáveis de ambiente para diferentes ambientes
- Valores padrão para desenvolvimento

### Inicialização de Dependências
- Repositórios são instanciados com configuração
- Services recebem repositórios via construtor
- Commands recebem services via importação

## Considerações de Performance

### Banco de Dados
- SQLite para simplicidade e portabilidade
- Índices automáticos em chaves primárias
- Transações para consistência

### Memória
- Processamento assíncrono com aiosqlite
- Limite configurável de mensagens do histórico
- Limpeza automática de dados antigos

## Segurança

### Validação de Entrada
- Validação de parâmetros nos commands
- Sanitização de dados antes de salvar
- Tratamento de exceções

### Acesso a Dados
- Prepared statements para prevenir SQL injection
- Transações para consistência
- Validação de tipos nos modelos
