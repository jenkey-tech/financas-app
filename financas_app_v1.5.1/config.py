"""Configurações e constantes do app de finanças."""

DB_FILE = "financas.db"
APP_VERSION = "1.5.1"
BACKUP_DIR = "backups"
EXPORT_DIR = "exports"

CATEGORIAS_PADRAO = [
    "Cartão Nubank", "Cartão Itaú dia 08", "Cartão Itaú dia 10", "Cartão Mercado Livre",
    "Água", "Energia", "Gás", "Internet", "Aluguel/Cond", "Escola Aria", "Escola bebes",
    "Diarista", "Condomínio Lumen", "IPTU Lumen", "Ifood", "Parcela Moveis", "Contador", "Emprestimo"
]

CONTAS_RECORRENTES = [
    {"categoria": "Cartão Itaú dia 08", "dia": 8, "tipo": "manual"},
    {"categoria": "Cartão Itaú dia 10", "dia": 10, "tipo": "manual"},
    {"categoria": "Cartão Nubank", "dia": 12, "tipo": "manual"},
    {"categoria": "Cartão Mercado Livre", "dia": 20, "tipo": "manual"},
    {"categoria": "Água", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Energia", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Gás", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Internet", "dia": None, "tipo": "debito automatico"},
    {"categoria": "Aluguel/Cond", "dia": 20, "tipo": "manual"},
    {"categoria": "Escola Aria", "dia": 10, "tipo": "manual"},
    {"categoria": "Contador", "dia": 10, "tipo": "manual"},
    {"categoria": "Parcela Moveis", "dia": 10, "tipo": "manual"},
    {"categoria": "Escola bebes", "dia": 30, "tipo": "manual"},
    {"categoria": "Condomínio Lumen", "dia": 5, "tipo": "manual"},
    {"categoria": "IPTU Lumen", "dia": 20, "tipo": "manual"},
    {"categoria": "Emprestimo", "dia": 8, "tipo": "manual"},
]

CATEGORIAS_ACUMULATIVAS = {
    "Ifood", "Cartão Nubank", "Cartão Itaú dia 08", "Cartão Itaú dia 10",
    "Cartão Mercado Livre", "Água", "Energia", "Gás", "Diarista"
}
CATEGORIAS_FIXAS = {
    "Aluguel/Cond", "Escola Aria", "Escola bebes", "Contador", "Parcela Moveis",
    "Emprestimo", "Condomínio Lumen", "IPTU Lumen", "Internet"
}
CARTOES = ["Cartão Nubank", "Cartão Itaú dia 08", "Cartão Itaú dia 10", "Cartão Mercado Livre"]
FIXOS = ["Aluguel/Cond", "Escola Aria", "Escola bebes", "Internet", "Parcela Moveis", "Contador", "Emprestimo", "Condomínio Lumen", "IPTU Lumen"]

DADOS_INICIAIS = [
    ("2025-01", "Cartão Nubank", 1050.35), ("2025-01", "Cartão Itaú dia 10", 7585.25), ("2025-01", "Energia", 380.39), ("2025-01", "Gás", 54.52), ("2025-01", "Internet", 109.80), ("2025-01", "Aluguel/Cond", 3976), ("2025-01", "Escola Aria", 2065.43), ("2025-01", "Escola bebes", 2200), ("2025-01", "Parcela Moveis", 350), ("2025-01", "Contador", 3879),
    ("2025-02", "Cartão Nubank", 1261.33), ("2025-02", "Cartão Itaú dia 10", 5071.72), ("2025-02", "Energia", 278.57), ("2025-02", "Gás", 78.13), ("2025-02", "Internet", 109.80), ("2025-02", "Aluguel/Cond", 4320), ("2025-02", "Escola Aria", 2065.43), ("2025-02", "Escola bebes", 2200), ("2025-02", "Ifood", 380), ("2025-02", "Parcela Moveis", 50),
    ("2025-03", "Cartão Nubank", 1091.30), ("2025-03", "Cartão Itaú dia 10", 7506.86), ("2025-03", "Energia", 396.68), ("2025-03", "Gás", 85.87), ("2025-03", "Internet", 109.80), ("2025-03", "Aluguel/Cond", 4320), ("2025-03", "Escola Aria", 2065.43), ("2025-03", "Escola bebes", 2200), ("2025-03", "Ifood", 350),
    ("2025-04", "Cartão Nubank", 692.04), ("2025-04", "Cartão Itaú dia 10", 9107.40), ("2025-04", "Cartão Mercado Livre", 224.77), ("2025-04", "Energia", 358.51), ("2025-04", "Gás", 69.12), ("2025-04", "Internet", 109.80), ("2025-04", "Aluguel/Cond", 4320), ("2025-04", "Escola Aria", 1346.18), ("2025-04", "Escola bebes", 2200), ("2025-04", "Condomínio Lumen", 1338), ("2025-04", "Ifood", 336),
    ("2025-05", "Cartão Nubank", 1019.72), ("2025-05", "Cartão Itaú dia 10", 11778.15), ("2025-05", "Cartão Mercado Livre", 3034.54), ("2025-05", "Energia", 379.46), ("2025-05", "Gás", 113.71), ("2025-05", "Internet", 109.80), ("2025-05", "Aluguel/Cond", 4320), ("2025-05", "Escola Aria", 1346.18), ("2025-05", "Escola bebes", 2200), ("2025-05", "Condomínio Lumen", 1338),
    ("2025-06", "Cartão Nubank", 4202.62), ("2025-06", "Cartão Itaú dia 10", 10389.39), ("2025-06", "Cartão Mercado Livre", 334), ("2025-06", "Energia", 410.06), ("2025-06", "Gás", 112.98), ("2025-06", "Internet", 109.80), ("2025-06", "Aluguel/Cond", 4320), ("2025-06", "Escola Aria", 1346.18), ("2025-06", "Escola bebes", 2200), ("2025-06", "Condomínio Lumen", 1338), ("2025-06", "Parcela Moveis", 1882.35),
    ("2025-07", "Cartão Nubank", 4676.02), ("2025-07", "Cartão Itaú dia 10", 11022.48), ("2025-07", "Cartão Mercado Livre", 334), ("2025-07", "Energia", 442.11), ("2025-07", "Gás", 59.87), ("2025-07", "Internet", 109.80), ("2025-07", "Aluguel/Cond", 4320), ("2025-07", "Escola Aria", 1346.18), ("2025-07", "Escola bebes", 2200), ("2025-07", "Condomínio Lumen", 1338), ("2025-07", "Parcela Moveis", 1882.35),
    ("2025-08", "Cartão Nubank", 5914.53), ("2025-08", "Cartão Itaú dia 10", 11398.11), ("2025-08", "Cartão Mercado Livre", 469.76), ("2025-08", "Energia", 351.88), ("2025-08", "Gás", 77.92), ("2025-08", "Internet", 109.80), ("2025-08", "Aluguel/Cond", 4320), ("2025-08", "Escola Aria", 1346.18), ("2025-08", "Escola bebes", 2200), ("2025-08", "Condomínio Lumen", 1338), ("2025-08", "Parcela Moveis", 1882.35), ("2025-08", "Contador", 320),
    ("2025-09", "Cartão Nubank", 935), ("2025-09", "Cartão Itaú dia 10", 8831.01), ("2025-09", "Cartão Mercado Livre", 586.35), ("2025-09", "Energia", 347.14), ("2025-09", "Gás", 70.28), ("2025-09", "Internet", 109.80), ("2025-09", "Aluguel/Cond", 4320), ("2025-09", "Escola Aria", 1346.18), ("2025-09", "Escola bebes", 2200), ("2025-09", "Condomínio Lumen", 1410), ("2025-09", "Parcela Moveis", 1882.35), ("2025-09", "Contador", 320),
    ("2025-10", "Cartão Nubank", 9813.31), ("2025-10", "Cartão Itaú dia 10", 6332.58), ("2025-10", "Cartão Mercado Livre", 363), ("2025-10", "Energia", 450.54), ("2025-10", "Internet", 113.58), ("2025-10", "Aluguel/Cond", 4320), ("2025-10", "Escola Aria", 1346.18), ("2025-10", "Escola bebes", 2200), ("2025-10", "Condomínio Lumen", 1418), ("2025-10", "Parcela Moveis", 1882.35), ("2025-10", "Contador", 320),
    ("2025-11", "Cartão Nubank", 12935.28), ("2025-11", "Cartão Itaú dia 10", 9799.77), ("2025-11", "Cartão Mercado Livre", 628.55), ("2025-11", "Energia", 526.73), ("2025-11", "Gás", 78.22), ("2025-11", "Internet", 114.90), ("2025-11", "Aluguel/Cond", 4320), ("2025-11", "Escola Aria", 1346.18), ("2025-11", "Escola bebes", 2200), ("2025-11", "Condomínio Lumen", 1418), ("2025-11", "Parcela Moveis", 1882.35), ("2025-11", "Contador", 320),
    ("2025-12", "Cartão Nubank", 10475.99), ("2025-12", "Cartão Itaú dia 10", 9442.72), ("2025-12", "Cartão Mercado Livre", 304.51), ("2025-12", "Energia", 383.96), ("2025-12", "Gás", 106.94), ("2025-12", "Internet", 114.90), ("2025-12", "Aluguel/Cond", 4320), ("2025-12", "Escola Aria", 5822), ("2025-12", "Escola bebes", 2200), ("2025-12", "Condomínio Lumen", 1440), ("2025-12", "Parcela Moveis", 1882.35), ("2025-12", "Contador", 320), ("2025-12", "Emprestimo", 681),
    ("2026-01", "Cartão Nubank", 7540.12), ("2026-01", "Cartão Itaú dia 10", 7490.99), ("2026-01", "Cartão Mercado Livre", 1294.53), ("2026-01", "Energia", 354.55), ("2026-01", "Gás", 12.40), ("2026-01", "Internet", 114.90), ("2026-01", "Aluguel/Cond", 4320), ("2026-01", "Escola Aria", 2466.38), ("2026-01", "Escola bebes", 2500), ("2026-01", "Diarista", 500), ("2026-01", "Condomínio Lumen", 1440.51), ("2026-01", "Parcela Moveis", 1882.35), ("2026-01", "Contador", 320), ("2026-01", "Emprestimo", 2702.07),
    ("2026-02", "Cartão Nubank", 7474.24), ("2026-02", "Cartão Itaú dia 10", 8723.24), ("2026-02", "Cartão Mercado Livre", 497.69), ("2026-02", "Energia", 229.69), ("2026-02", "Gás", 116), ("2026-02", "Internet", 114.90), ("2026-02", "Aluguel/Cond", 4340), ("2026-02", "Escola Aria", 2466.38), ("2026-02", "Escola bebes", 2500), ("2026-02", "Diarista", 500), ("2026-02", "Condomínio Lumen", 1440.51), ("2026-02", "Parcela Moveis", 1882.35), ("2026-02", "Ifood", 750), ("2026-02", "Contador", 320), ("2026-02", "Emprestimo", 2702.07),
    ("2026-03", "Cartão Nubank", 9679.39), ("2026-03", "Cartão Itaú dia 10", 9345.31), ("2026-03", "Cartão Mercado Livre", 686.27), ("2026-03", "Energia", 842.86), ("2026-03", "Gás", 160.24), ("2026-03", "Internet", 183.90), ("2026-03", "Aluguel/Cond", 4950), ("2026-03", "Escola Aria", 2466.38), ("2026-03", "Escola bebes", 2500), ("2026-03", "Diarista", 0), ("2026-03", "Condomínio Lumen", 1450.34), ("2026-03", "Parcela Moveis", 1882.35), ("2026-03", "Contador", 320), ("2026-03", "Emprestimo", 0),
    ("2026-04", "Cartão Nubank", 7071.89), ("2026-04", "Cartão Itaú dia 10", 6265.93), ("2026-04", "Cartão Mercado Livre", 300.34), ("2026-04", "Energia", 797.61), ("2026-04", "Gás", 90.08), ("2026-04", "Internet", 114.90), ("2026-04", "Aluguel/Cond", 4950), ("2026-04", "Escola Aria", 2518.99), ("2026-04", "Escola bebes", 2500), ("2026-04", "Diarista", 0), ("2026-04", "Condomínio Lumen", 1105.55), ("2026-04", "Parcela Moveis", 1882.35), ("2026-04", "Ifood", 700), ("2026-04", "Contador", 320), ("2026-04", "Emprestimo", 490.43),
]
