"""Configurações e constantes do app de finanças.

Categorias e valores abaixo são fictícios, apenas para demonstração
em instalações novas (seed via DADOS_INICIAIS). Não commitar dados reais.
"""

DB_FILE = "financas.db"
APP_VERSION = "3.4.3"
BACKUP_DIR = "backups"
EXPORT_DIR = "exports"

CATEGORIAS_PADRAO = [
    "Cartão Alpha", "Cartão Beta dia 08", "Cartão Beta dia 15", "Cartão Loja Online",
    "Água", "Energia", "Gás", "Internet", "Aluguel", "Escola", "Creche",
    "Diarista", "Condomínio", "IPTU", "Delivery", "Parcela Móveis", "Contador", "Empréstimo"
]

CONTAS_RECORRENTES = [
    {"categoria": "Cartão Beta dia 08", "dia": 8, "tipo": "manual"},
    {"categoria": "Cartão Beta dia 15", "dia": 15, "tipo": "manual"},
    {"categoria": "Cartão Alpha", "dia": 12, "tipo": "manual"},
    {"categoria": "Cartão Loja Online", "dia": 20, "tipo": "manual"},
    {"categoria": "Água", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Energia", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Gás", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Internet", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Aluguel", "dia": 5, "tipo": "manual"},
    {"categoria": "Escola", "dia": 10, "tipo": "manual"},
    {"categoria": "Contador", "dia": 10, "tipo": "manual"},
    {"categoria": "Parcela Móveis", "dia": 10, "tipo": "manual"},
    {"categoria": "Creche", "dia": 30, "tipo": "manual"},
    {"categoria": "Condomínio", "dia": 5, "tipo": "manual"},
    {"categoria": "IPTU", "dia": 20, "tipo": "manual"},
    {"categoria": "Empréstimo", "dia": 8, "tipo": "manual"},
]

CATEGORIAS_ACUMULATIVAS = {
    "Delivery", "Cartão Alpha", "Cartão Beta dia 08", "Cartão Beta dia 15",
    "Cartão Loja Online", "Água", "Energia", "Gás", "Diarista"
}
CATEGORIAS_FIXAS = {
    "Aluguel", "Escola", "Creche", "Contador", "Parcela Móveis",
    "Empréstimo", "Condomínio", "IPTU", "Internet"
}
CARTOES = ["Cartão Alpha", "Cartão Beta dia 08", "Cartão Beta dia 15", "Cartão Loja Online"]
FIXOS = ["Aluguel", "Escola", "Creche", "Internet", "Parcela Móveis", "Contador", "Empréstimo", "Condomínio", "IPTU"]

# Dados fictícios inseridos somente quando o banco local está vazio (primeira execução).
DADOS_INICIAIS = [
    ("2025-01", "Cartão Alpha", 850.00),
    ("2025-01", "Cartão Beta dia 15", 1200.00),
    ("2025-01", "Energia", 180.50),
    ("2025-01", "Gás", 45.00),
    ("2025-01", "Internet", 99.90),
    ("2025-01", "Aluguel", 2200.00),
    ("2025-01", "Escola", 1500.00),
    ("2025-01", "Condomínio", 650.00),
    ("2025-02", "Cartão Alpha", 920.00),
    ("2025-02", "Cartão Beta dia 15", 980.00),
    ("2025-02", "Energia", 165.00),
    ("2025-02", "Internet", 99.90),
    ("2025-02", "Aluguel", 2200.00),
    ("2025-02", "Escola", 1500.00),
    ("2025-02", "Delivery", 120.00),
    ("2025-03", "Cartão Alpha", 780.00),
    ("2025-03", "Energia", 190.00),
    ("2025-03", "Aluguel", 2200.00),
    ("2025-03", "Escola", 1500.00),
    ("2025-03", "Delivery", 95.00),
]
