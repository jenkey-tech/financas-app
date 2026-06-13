
import csv
import sqlite3
import statistics
import calendar
import os
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, date

DB_FILE = "financas.db"
APP_VERSION = "1.4.0"
BACKUP_DIR = "backups"
EXPORT_DIR = "exports"


try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False

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

def brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def parse_valor(txt):
    txt = str(txt).strip().replace("R$", "").replace(" ", "")
    if not txt:
        return 0.0
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None

def due_date_for_month(mes, dia):
    if dia is None:
        return None
    ano, mes_num = map(int, mes.split("-"))
    ultimo_dia = calendar.monthrange(ano, mes_num)[1]
    return date(ano, mes_num, min(dia, ultimo_dia))

def status_pagamento(mes, valor, status_lancamento, dia, tipo):
    venc = due_date_for_month(mes, dia)
    hoje = date.today()
    lancado = valor is not None
    vencido = bool(venc and venc < hoje)
    if not lancado:
        if tipo == "debito automatico":
            return "Débito automático"
        if vencido:
            return "⚠ Vencido sem lançamento"
        return "Não lançado"
    if status_lancamento == "Pago":
        return "Pago"
    if status_lancamento == "Débito automático":
        return "Débito automático"
    if vencido:
        return "⚠ Não pago vencido"
    return "Não pago"


def db_path():
    return Path(DB_FILE)

def backup_database(motivo="auto"):
    origem = db_path()
    if not origem.exists():
        return None
    Path(BACKUP_DIR).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = Path(BACKUP_DIR) / f"financas_{motivo}_{timestamp}.db"
    shutil.copy2(origem, destino)
    return destino

def export_snapshot_csv():
    Path(EXPORT_DIR).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = Path(EXPORT_DIR) / f"lancamentos_{timestamp}.csv"
    rows = query("SELECT mes,categoria,valor,status_lancamento,observacao FROM lancamentos ORDER BY mes,categoria")
    with open(destino, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["mes", "categoria", "valor", "status_lancamento", "observacao"])
        writer.writerows(rows)
    return destino

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT DEFAULT '',
            status_lancamento TEXT DEFAULT 'Pago',
            UNIQUE(mes, categoria)
        )
    """)
    try:
        cur.execute("ALTER TABLE lancamentos ADD COLUMN status_lancamento TEXT DEFAULT 'Pago'")
    except sqlite3.OperationalError:
        pass
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT DEFAULT ''
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_alvo REAL NOT NULL,
            valor_atual REAL DEFAULT 0,
            observacao TEXT DEFAULT ''
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            dia_vencimento INTEGER,
            tipo TEXT DEFAULT 'manual',
            recorrente INTEGER DEFAULT 0,
            ativa INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pendencias_ignoradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            categoria TEXT NOT NULL,
            vencimento TEXT NOT NULL,
            motivo TEXT DEFAULT 'regularizado',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mes, categoria, vencimento)
        )
    """)
    for conta in CONTAS_RECORRENTES:
        cur.execute("""
            INSERT OR IGNORE INTO categorias (nome, dia_vencimento, tipo, recorrente, ativa)
            VALUES (?, ?, ?, 1, 1)
        """, (conta["categoria"], conta["dia"], conta["tipo"]))
    for nome in CATEGORIAS_PADRAO:
        cur.execute("""
            INSERT OR IGNORE INTO categorias (nome, dia_vencimento, tipo, recorrente, ativa)
            VALUES (?, NULL, 'manual', 0, 1)
        """, (nome,))

    cur.execute("UPDATE lancamentos SET categoria='Cartão Nubank' WHERE categoria='Cartão Gui'")
    cur.execute("UPDATE lancamentos SET categoria='Cartão Itaú dia 10' WHERE categoria='Cartão Itau'")
    cur.execute("UPDATE lancamentos SET categoria='Condomínio Lumen' WHERE categoria='Cond/IPTU'")
    cur.execute("SELECT COUNT(*) FROM lancamentos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT OR REPLACE INTO lancamentos (mes, categoria, valor, status_lancamento) VALUES (?, ?, ?, 'Pago')",
            DADOS_INICIAIS
        )
    con.commit()
    con.close()

def query(sql, params=()):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows

def execute(sql, params=()):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, params)
    con.commit()
    con.close()

def get_categories(active_only=True):
    where = "WHERE ativa=1" if active_only else ""
    rows = query(f"""
        SELECT nome, dia_vencimento, tipo, recorrente, ativa
        FROM categorias
        {where}
        ORDER BY nome
    """)
    if not rows:
        return [(nome, None, "manual", 0, 1) for nome in sorted(CATEGORIAS_PADRAO)]
    return rows

def get_category_names(active_only=True):
    nomes = [r[0] for r in get_categories(active_only)]
    extras = [r[0] for r in query("SELECT DISTINCT categoria FROM lancamentos ORDER BY categoria")]
    for nome in extras:
        if nome not in nomes:
            nomes.append(nome)
    return sorted(nomes)

def get_recurring_categories():
    rows = query("""
        SELECT nome, dia_vencimento, tipo
        FROM categorias
        WHERE recorrente=1 AND ativa=1
        ORDER BY COALESCE(dia_vencimento, 99), nome
    """)
    if not rows:
        return CONTAS_RECORRENTES
    return [{"categoria": nome, "dia": dia, "tipo": tipo or "manual"} for nome, dia, tipo in rows]

def upsert_category(nome, dia_vencimento=None, tipo="manual", recorrente=0, ativa=1):
    execute("""
        INSERT INTO categorias (nome, dia_vencimento, tipo, recorrente, ativa)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(nome) DO UPDATE SET
            dia_vencimento=excluded.dia_vencimento,
            tipo=excluded.tipo,
            recorrente=excluded.recorrente,
            ativa=excluded.ativa
    """, (nome, dia_vencimento, tipo, int(recorrente), int(ativa)))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Finanças Pessoais - v{APP_VERSION}")
        self.geometry("1300x820")
        self.minsize(1100, 700)
        self.configure(bg="#f4f6fb")
        self.suggested_value = None
        self.setup_style()
        self.create_layout()
        self.refresh_all()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f6fb")
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background="#f4f6fb", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("White.TLabel", background="white", foreground="#1f2937", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), background="#f4f6fb")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), background="white")
        style.configure("CardValue.TLabel", font=("Segoe UI", 18, "bold"), background="white", foreground="#111827")
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=28, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(16, 8))

    def create_layout(self):
        top = ttk.Frame(self, padding=18)
        top.pack(fill="x")
        ttk.Label(top, text="Painel de Finanças", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Backup + Git", command=self.git_backup_push).pack(side="right", padx=4)
        ttk.Button(top, text="Backup", command=self.manual_backup).pack(side="right", padx=4)
        ttk.Button(top, text="Importar CSV", command=self.import_csv).pack(side="right", padx=4)
        ttk.Button(top, text="Exportar CSV", command=self.export_csv).pack(side="right", padx=4)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.tab_entries = ttk.Frame(self.notebook, padding=12)
        self.tab_insights = ttk.Frame(self.notebook, padding=12)
        self.tab_cashflow = ttk.Frame(self.notebook, padding=12)
        self.tab_goals = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_entries, text="Lançamentos")
        self.notebook.add(self.tab_insights, text="Insights e gráficos")
        self.notebook.add(self.tab_cashflow, text="Fluxo de caixa")
        self.notebook.add(self.tab_goals, text="Metas")
        self.create_entries_tab()
        self.create_insights_tab()
        self.create_cashflow_tab()
        self.create_goals_tab()

    def card(self, parent, title, value):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        lbl = ttk.Label(frame, text=value, style="CardValue.TLabel")
        lbl.pack(anchor="w", pady=(8, 0))
        frame.value_label = lbl
        return frame

    def create_entries_tab(self):
        cards = ttk.Frame(self.tab_entries)
        cards.pack(fill="x", pady=(0, 10))
        self.card_total = self.card(cards, "Total do mês filtrado", "R$ 0,00")
        self.card_media = self.card(cards, "Média mensal geral", "R$ 0,00")
        self.card_maior = self.card(cards, "Maior gasto do mês", "-")
        self.card_total.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.card_media.pack(side="left", fill="x", expand=True, padx=6)
        self.card_maior.pack(side="left", fill="x", expand=True, padx=(6, 0))

        filter_box = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=10)
        filter_box.pack(fill="x", pady=(0, 10))
        ttk.Label(filter_box, text="Visualizar mês", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.filter_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.filter_month_combo = ttk.Combobox(filter_box, textvariable=self.filter_month_var, width=12)
        self.filter_month_combo.grid(row=1, column=0, sticky="w")
        self.filter_month_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_all())
        self.filter_month_combo.bind("<Return>", lambda e: self.refresh_all())
        ttk.Button(filter_box, text="Mês vigente", command=self.current_month).grid(row=1, column=1, padx=6)
        ttk.Button(filter_box, text="Lançar próximo mês", command=self.launch_next_month).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        form = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=10)
        form.pack(fill="x", pady=(0, 10))
        ttk.Label(form, text="Novo/editar lançamento", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))
        ttk.Button(form, text="Gerenciar categorias", command=self.open_category_manager).grid(row=0, column=5, columnspan=2, sticky="e", padx=6)

        today = datetime.now()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=f"{today.month:02d}")
        self.cat_var = tk.StringVar(value=CATEGORIAS_PADRAO[0])
        self.value_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pago")
        self.obs_var = tk.StringVar()
        self.suggestion_var = tk.StringVar(value="Selecione uma categoria para ver sugestão.")

        labels = ["Ano", "Mês", "Categoria", "Valor", "Status", "Obs."]
        for i, label in enumerate(labels):
            ttk.Label(form, text=label, style="White.TLabel").grid(row=1, column=i, sticky="w")

        ttk.Combobox(form, textvariable=self.year_var, values=[str(a) for a in range(2024, today.year+5)], width=8, state="readonly").grid(row=2, column=0, padx=(0,6), sticky="w")
        ttk.Combobox(form, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1,13)], width=6, state="readonly").grid(row=2, column=1, padx=6, sticky="w")
        self.cat_combo = ttk.Combobox(form, textvariable=self.cat_var, values=get_category_names(), width=26)
        self.cat_combo.grid(row=2, column=2, padx=6, sticky="w")
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.update_suggestion())
        self.cat_combo.bind("<KeyRelease>", lambda e: self.update_suggestion())
        ttk.Entry(form, textvariable=self.value_var, width=14).grid(row=2, column=3, padx=6, sticky="w")
        ttk.Combobox(form, textvariable=self.status_var, values=["Pago", "Não pago", "Débito automático"], width=16, state="readonly").grid(row=2, column=4, padx=6, sticky="w")
        ttk.Entry(form, textvariable=self.obs_var, width=26).grid(row=2, column=5, padx=6, sticky="w")

        buttons = ttk.Frame(form, style="Card.TFrame")
        buttons.grid(row=3, column=0, columnspan=8, sticky="w", pady=(10, 0))
        ttk.Button(buttons, text="Salvar", command=self.save_entry).pack(side="left", padx=(0, 6))

        ttk.Button(buttons, text="Usar sugestão", command=self.use_suggestion).pack(side="left", padx=6)
        ttk.Button(buttons, text="Excluir selecionado", command=self.delete_entry).pack(side="left", padx=6)
        ttk.Label(form, textvariable=self.suggestion_var, style="White.TLabel").grid(row=4, column=0, columnspan=8, sticky="w", pady=(8, 0))

        pay_box = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=10)
        pay_box.pack(fill="both", expand=True, pady=(0, 10))
        ttk.Label(pay_box, text="Controle de pagamentos do mês", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        pay_container = ttk.Frame(pay_box, style="Card.TFrame")
        pay_container.pack(fill="both", expand=True)
        self.pay_tree = ttk.Treeview(pay_container, columns=("status", "categoria", "vencimento", "valor", "tipo"), show="headings", height=8)
        pay_scroll = ttk.Scrollbar(pay_container, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=pay_scroll.set)
        self.pay_tree.pack(side="left", fill="both", expand=True)
        pay_scroll.pack(side="right", fill="y")

        self.pay_sort_state = {"column": None, "reverse": False}
        for col, label, width in [("status","Status",180),("categoria","Conta",230),("vencimento","Vencimento",120),("valor","Valor",120),("tipo","Tipo",150)]:
            self.pay_tree.heading(col, text=label, command=lambda c=col: self.sort_pay_tree(c))
            self.pay_tree.column(col, width=width, anchor="e" if col == "valor" else "w", stretch=True)

        self.pay_tree.tag_configure("Pago", background="#16a34a", foreground="white")
        self.pay_tree.tag_configure("Débito automático", background="#facc15", foreground="#111827")
        self.pay_tree.tag_configure("Não lançado", background="#facc15", foreground="#111827")
        self.pay_tree.tag_configure("⚠ Vencido sem lançamento", background="#f97316", foreground="white")
        self.pay_tree.tag_configure("Não pago", background="#ef4444", foreground="white")
        self.pay_tree.tag_configure("⚠ Não pago vencido", background="#b91c1c", foreground="white")
        self.pay_tree.bind("<Double-1>", self.fill_payment_from_selection)
        self.pay_tree.bind("<Button-3>", self.show_payment_context_menu)

        self.payment_menu = tk.Menu(self, tearoff=0)
        self.payment_menu.add_command(label="Editar célula", command=self.edit_clicked_payment_cell)
        self.payment_menu.add_command(label="Editar lançamento", command=self.fill_payment_from_selection)
        self.payment_menu.add_separator()
        self.payment_menu.add_command(label="Deletar lançamento", command=self.delete_payment_record)

        ttk.Label(pay_box, text="Vencidos e próximos 7 dias", style="CardTitle.TLabel").pack(anchor="w", pady=(12, 8))
        self.upcoming_tree = ttk.Treeview(pay_box, columns=("data", "conta", "status", "valor"), show="headings", height=4)
        for col, label, width in [("data", "Data", 110), ("conta", "Conta", 260), ("status", "Status", 180), ("valor", "Valor", 120)]:
            self.upcoming_tree.heading(col, text=label)
            self.upcoming_tree.column(col, width=width, anchor="e" if col == "valor" else "w")
        self.upcoming_tree.tag_configure("alerta", background="#f97316", foreground="white")
        self.upcoming_tree.tag_configure("ok", background="#dcfce7", foreground="#111827")
        self.upcoming_tree.pack(fill="x")
        self.upcoming_tree.bind("<Button-3>", self.show_upcoming_context_menu)
        self.upcoming_menu = tk.Menu(self, tearoff=0)
        self.upcoming_menu.add_command(label="Regularizar/ignorar pendência", command=self.ignore_upcoming_pending)

        table_box = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=10)
        table_box.pack(fill="both", expand=True)
        ttk.Label(table_box, text="Lançamentos", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.tree = ttk.Treeview(table_box, columns=("mes","categoria","valor","status","obs"), show="headings", height=7)
        for col, label, width in [("mes","Mês",90),("categoria","Categoria",230),("valor","Valor",120),("status","Status",130),("obs","Obs.",240)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="e" if col=="valor" else "w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.fill_form_from_selection)

    def create_insights_tab(self):
        top = ttk.Frame(self.tab_insights, style="Card.TFrame", padding=12)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="Período analisado", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0,8))

        self.insight_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.insight_start_var = tk.StringVar(value="")
        self.insight_end_var = tk.StringVar(value="")
        self.insight_all_var = tk.BooleanVar(value=False)

        ttk.Label(top, text="Mês", style="White.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(top, text="De", style="White.TLabel").grid(row=1, column=1, sticky="w", padx=(12, 0))
        ttk.Label(top, text="Até", style="White.TLabel").grid(row=1, column=2, sticky="w", padx=(12, 0))

        self.insight_month_combo = ttk.Combobox(top, textvariable=self.insight_month_var, width=12)
        self.insight_month_combo.grid(row=2, column=0, sticky="w")
        self.insight_month_combo.bind("<<ComboboxSelected>>", lambda e: self.select_single_insight_month())

        self.insight_start_combo = ttk.Combobox(top, textvariable=self.insight_start_var, width=12)
        self.insight_start_combo.grid(row=2, column=1, sticky="w", padx=(12, 0))
        self.insight_start_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_insights())

        self.insight_end_combo = ttk.Combobox(top, textvariable=self.insight_end_var, width=12)
        self.insight_end_combo.grid(row=2, column=2, sticky="w", padx=(12, 0))
        self.insight_end_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_insights())

        ttk.Checkbutton(top, text="Ver todos", variable=self.insight_all_var, command=self.refresh_insights).grid(row=2, column=3, sticky="w", padx=14)
        ttk.Button(top, text="Aplicar intervalo", command=self.refresh_insights).grid(row=2, column=4, sticky="w", padx=6)

        self.proj_label = ttk.Label(top, text="", style="White.TLabel")
        self.proj_label.grid(row=3, column=0, columnspan=6, sticky="w", pady=(10, 0))

        body = ttk.Frame(self.tab_insights)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0,12))
        right = ttk.Frame(body, width=420)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        charts = [
            ("Evolução do total mensal", "trend_frame"),
            ("Top gastos do período", "top_frame"),
            ("Cartões x gastos fixos", "cards_fixed_frame"),
            ("Saúde financeira: receitas, despesas e saldo", "health_frame"),
        ]
        for title, attr in charts:
            card = ttk.Frame(left, style="Card.TFrame", padding=12)
            card.pack(fill="both", expand=True, pady=(0,12))
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            frame = ttk.Frame(card, style="Card.TFrame")
            frame.pack(fill="both", expand=True, pady=(8,0))
            setattr(self, attr, frame)

        txt_card = ttk.Frame(right, style="Card.TFrame", padding=12)
        txt_card.pack(fill="both", expand=True)
        ttk.Label(txt_card, text="Leitura rápida", style="CardTitle.TLabel").pack(anchor="w")
        self.insights_text = tk.Text(txt_card, wrap="word", bg="white", relief="flat", font=("Segoe UI", 10))
        self.insights_text.pack(fill="both", expand=True, pady=(8,0))

    def create_cashflow_tab(self):
        cards = ttk.Frame(self.tab_cashflow)
        cards.pack(fill="x", pady=(0, 12))
        self.cash_receitas_card = self.card(cards, "Receitas do mês", "R$ 0,00")
        self.cash_despesas_card = self.card(cards, "Despesas lançadas", "R$ 0,00")
        self.cash_saldo_card = self.card(cards, "Saldo projetado", "R$ 0,00")
        self.cash_receitas_card.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.cash_despesas_card.pack(side="left", fill="x", expand=True, padx=8)
        self.cash_saldo_card.pack(side="left", fill="x", expand=True, padx=(8, 0))

        form = ttk.Frame(self.tab_cashflow, style="Card.TFrame", padding=12)
        form.pack(fill="x", pady=(0, 12))
        ttk.Label(form, text="Nova receita", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=7, sticky="w", pady=(0, 8))
        for i, label in enumerate(["Ano", "Mês", "Descrição", "Valor", "Obs."]):
            ttk.Label(form, text=label, style="White.TLabel").grid(row=1, column=i, sticky="w")
        today = datetime.now()
        self.rec_year_var = tk.StringVar(value=str(today.year))
        self.rec_month_var = tk.StringVar(value=f"{today.month:02d}")
        self.rec_desc_var = tk.StringVar()
        self.rec_value_var = tk.StringVar()
        self.rec_obs_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.rec_year_var, values=[str(a) for a in range(2024, today.year+5)], width=8, state="readonly").grid(row=2, column=0, padx=(0,8))
        ttk.Combobox(form, textvariable=self.rec_month_var, values=[f"{m:02d}" for m in range(1,13)], width=6, state="readonly").grid(row=2, column=1, padx=8)
        ttk.Entry(form, textvariable=self.rec_desc_var, width=28).grid(row=2, column=2, padx=8)
        ttk.Entry(form, textvariable=self.rec_value_var, width=14).grid(row=2, column=3, padx=8)
        ttk.Entry(form, textvariable=self.rec_obs_var, width=28).grid(row=2, column=4, padx=8)
        ttk.Button(form, text="Salvar receita", command=self.save_income).grid(row=2, column=5, padx=6)
        ttk.Button(form, text="Excluir selecionada", command=self.delete_income).grid(row=2, column=6, padx=6)

        table_box = ttk.Frame(self.tab_cashflow, style="Card.TFrame", padding=12)
        table_box.pack(fill="both", expand=True)
        ttk.Label(table_box, text="Receitas", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.income_tree = ttk.Treeview(table_box, columns=("id", "mes", "descricao", "valor", "obs"), show="headings")
        for col, label, width in [("id", "ID", 50), ("mes", "Mês", 90), ("descricao", "Descrição", 250), ("valor", "Valor", 120), ("obs", "Obs.", 260)]:
            self.income_tree.heading(col, text=label)
            self.income_tree.column(col, width=width, anchor="e" if col == "valor" else "w")
        self.income_tree.pack(fill="both", expand=True)

    def create_goals_tab(self):
        form = ttk.Frame(self.tab_goals, style="Card.TFrame", padding=12)
        form.pack(fill="x", pady=(0, 12))
        ttk.Label(form, text="Meta financeira", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=7, sticky="w", pady=(0, 8))
        for i, label in enumerate(["Nome", "Valor alvo", "Valor atual", "Obs."]):
            ttk.Label(form, text=label, style="White.TLabel").grid(row=1, column=i, sticky="w")
        self.goal_name_var = tk.StringVar()
        self.goal_target_var = tk.StringVar()
        self.goal_current_var = tk.StringVar()
        self.goal_obs_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.goal_name_var, width=28).grid(row=2, column=0, padx=(0,8))
        ttk.Entry(form, textvariable=self.goal_target_var, width=14).grid(row=2, column=1, padx=8)
        ttk.Entry(form, textvariable=self.goal_current_var, width=14).grid(row=2, column=2, padx=8)
        ttk.Entry(form, textvariable=self.goal_obs_var, width=28).grid(row=2, column=3, padx=8)
        ttk.Button(form, text="Salvar meta", command=self.save_goal).grid(row=2, column=4, padx=6)
        ttk.Button(form, text="Excluir selecionada", command=self.delete_goal).grid(row=2, column=5, padx=6)

        table_box = ttk.Frame(self.tab_goals, style="Card.TFrame", padding=12)
        table_box.pack(fill="both", expand=True)
        ttk.Label(table_box, text="Metas cadastradas", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.goal_tree = ttk.Treeview(table_box, columns=("id", "nome", "alvo", "atual", "progresso", "obs"), show="headings")
        for col, label, width in [("id", "ID", 50), ("nome", "Meta", 240), ("alvo", "Alvo", 120), ("atual", "Atual", 120), ("progresso", "Progresso", 120), ("obs", "Obs.", 260)]:
            self.goal_tree.heading(col, text=label)
            self.goal_tree.column(col, width=width, anchor="e" if col in ("alvo", "atual", "progresso") else "w")
        self.goal_tree.pack(fill="both", expand=True)
        self.goal_tree.bind("<Double-1>", self.fill_goal_from_selection)

    def months_available(self):
        meses = [r[0] for r in query("SELECT DISTINCT mes FROM lancamentos ORDER BY mes DESC")]
        atual = datetime.now().strftime("%Y-%m")
        return [atual] + [m for m in meses if m != atual]

    def selected_filter_month(self):
        val = self.filter_month_var.get().strip()
        return None if val in ("", "Todos") else val

    def current_month(self):
        mes = datetime.now().strftime("%Y-%m")
        self.filter_month_var.set(mes)
        self.insight_month_var.set(mes)
        self.refresh_all()

    def clear_filter(self):
        self.filter_month_var.set("Todos")
        self.refresh_all()

    def get_suggested_value(self, categoria):
        rows = query("SELECT valor FROM lancamentos WHERE categoria=? AND valor > 0 ORDER BY mes DESC LIMIT 6", (categoria,))
        if not rows:
            return None, "Sem histórico para sugerir valor."
        valores = [r[0] for r in rows]
        ultimo = valores[0]
        media = statistics.mean(valores)
        if len(valores) >= 3 and len(set(round(v, 2) for v in valores[:3])) == 1:
            return ultimo, f"Valor recorrente sugerido: {brl(ultimo)}."
        return ultimo, f"Último valor: {brl(ultimo)} | Média recente: {brl(media)}."

    def update_suggestion(self):
        valor, texto = self.get_suggested_value(self.cat_var.get().strip())
        self.suggested_value = valor
        self.suggestion_var.set(texto)

    def use_suggestion(self):
        valor, texto = self.get_suggested_value(self.cat_var.get().strip())
        self.suggested_value = valor
        self.suggestion_var.set(texto)
        if valor is not None:
            self.value_var.set(brl(valor).replace("R$ ", ""))

    def decide_duplicate_action(self, categoria, existente, novo):
        if categoria in CATEGORIAS_ACUMULATIVAS:
            return "somar"
        resposta = messagebox.askyesnocancel(
            "Lançamento já existe",
            f"Já existe {categoria} neste mês com valor {brl(existente)}.\n\n"
            f"Sim = somar {brl(novo)} ao valor existente\n"
            f"Não = substituir pelo novo valor\n"
            f"Cancelar = não fazer nada"
        )
        if resposta is True:
            return "somar"
        if resposta is False:
            return "substituir"
        return "cancelar"

    def refresh_category_combobox(self):
        if hasattr(self, "cat_combo"):
            self.cat_combo["values"] = get_category_names()

    def open_category_manager(self):
        win = tk.Toplevel(self)
        win.title("Gerenciar categorias")
        win.geometry("860x520")
        win.configure(bg="#f4f6fb")
        win.transient(self)

        form = ttk.Frame(win, style="Card.TFrame", padding=12)
        form.pack(fill="x", padx=12, pady=12)

        ttk.Label(form, text="Categoria", style="White.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Dia venc.", style="White.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Tipo", style="White.TLabel").grid(row=0, column=2, sticky="w")
        ttk.Label(form, text="Recorrência", style="White.TLabel").grid(row=0, column=3, sticky="w")

        nome_var = tk.StringVar()
        dia_var = tk.StringVar()
        tipo_var = tk.StringVar(value="manual")
        recorrencia_var = tk.StringVar(value="Somente mês específico")

        nome_entry = ttk.Entry(form, textvariable=nome_var, width=28)
        nome_entry.grid(row=1, column=0, padx=(0, 8), sticky="w")
        ttk.Entry(form, textvariable=dia_var, width=8).grid(row=1, column=1, padx=8, sticky="w")
        ttk.Combobox(form, textvariable=tipo_var, values=["manual", "debito automatico"], width=18, state="readonly").grid(row=1, column=2, padx=8, sticky="w")
        ttk.Combobox(form, textvariable=recorrencia_var, values=["Recorrente", "Somente mês específico"], width=22, state="readonly").grid(row=1, column=3, padx=8, sticky="w")

        list_frame = ttk.Frame(win, style="Card.TFrame", padding=12)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        tree = ttk.Treeview(list_frame, columns=("nome", "dia", "tipo", "recorrente", "ativa"), show="headings")
        for col, label, width in [
            ("nome", "Categoria", 260),
            ("dia", "Dia venc.", 90),
            ("tipo", "Tipo", 160),
            ("recorrente", "Recorrente", 110),
            ("ativa", "Ativa", 80),
        ]:
            tree.heading(col, text=label)
            tree.column(col, width=width, anchor="w")
        tree.pack(fill="both", expand=True)

        def carregar():
            for i in tree.get_children():
                tree.delete(i)
            for nome, dia, tipo, recorrente, ativa in get_categories(active_only=False):
                tree.insert("", "end", values=(nome, "" if dia is None else dia, tipo, "Sim" if recorrente else "Não", "Sim" if ativa else "Não"))

        def preencher(event=None):
            item = tree.selection()
            if not item:
                return
            nome, dia, tipo, recorrente, ativa = tree.item(item[0], "values")
            nome_var.set(nome)
            dia_var.set(str(dia) if dia else "")
            tipo_var.set(tipo or "manual")
            recorrencia_var.set("Recorrente" if recorrente == "Sim" else "Somente mês específico")

        def salvar():
            nome = nome_var.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Informe o nome da categoria.")
                return
            dia_txt = dia_var.get().strip()
            dia = None
            if dia_txt:
                try:
                    dia = int(dia_txt)
                    if dia < 1 or dia > 31:
                        raise ValueError
                except ValueError:
                    messagebox.showerror("Erro", "Dia de vencimento deve ser entre 1 e 31.")
                    return
            tipo = tipo_var.get()
            recorrente = 1 if recorrencia_var.get() == "Recorrente" else 0
            backup_database("antes_categoria")
            upsert_category(nome, dia, tipo, recorrente, 1)
            if nome not in CATEGORIAS_PADRAO:
                CATEGORIAS_PADRAO.append(nome)
                CATEGORIAS_PADRAO.sort()
            self.refresh_category_combobox()

            # Se for somente mês específico, cria/garante lançamento no mês filtrado.
            if not recorrente:
                mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")
                existe = query("SELECT 1 FROM lancamentos WHERE mes=? AND categoria=?", (mes, nome))
                if not existe:
                    status = "Débito automático" if tipo == "debito automatico" else "Não pago"
                    execute("""
                        INSERT INTO lancamentos (mes, categoria, valor, observacao, status_lancamento)
                        VALUES (?, ?, 0, 'Categoria criada para este mês', ?)
                    """, (mes, nome, status))
            carregar()
            self.refresh_all()
            messagebox.showinfo("Categorias", "Categoria salva.")

        def editar_lancamentos_nome_antigo():
            item = tree.selection()
            if not item:
                return
            antigo = tree.item(item[0], "values")[0]
            novo = nome_var.get().strip()
            if not novo or novo == antigo:
                return
            if messagebox.askyesno("Renomear lançamentos", f"Atualizar lançamentos antigos de '{antigo}' para '{novo}'?"):
                backup_database("antes_renomear_categoria")
                execute("UPDATE lancamentos SET categoria=? WHERE categoria=?", (novo, antigo))
                self.refresh_all()
                carregar()

        def desativar():
            item = tree.selection()
            if not item:
                return
            nome = tree.item(item[0], "values")[0]
            if messagebox.askyesno("Desativar categoria", f"Desativar '{nome}'? Os lançamentos antigos serão mantidos."):
                backup_database("antes_desativar_categoria")
                execute("UPDATE categorias SET ativa=0 WHERE nome=?", (nome,))
                self.refresh_category_combobox()
                self.refresh_all()
                carregar()

        btns = ttk.Frame(form, style="Card.TFrame")
        btns.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Button(btns, text="Salvar categoria", command=salvar).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Renomear lançamentos antigos", command=editar_lancamentos_nome_antigo).pack(side="left", padx=6)
        ttk.Button(btns, text="Desativar", command=desativar).pack(side="left", padx=6)
        ttk.Button(btns, text="Limpar", command=lambda: (nome_var.set(""), dia_var.set(""), tipo_var.set("manual"), recorrencia_var.set("Somente mês específico"))).pack(side="left", padx=6)

        tree.bind("<<TreeviewSelect>>", preencher)
        tree.bind("<Double-1>", preencher)
        carregar()
        nome_entry.focus_set()

    def next_month_value(self, mes):
        ano, mes_num = map(int, mes.split("-"))
        if mes_num == 12:
            return f"{ano+1}-01"
        return f"{ano}-{mes_num+1:02d}"

    def launch_next_month(self):
        base_mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")
        prox_mes = self.next_month_value(base_mes)
        if not messagebox.askyesno("Lançar próximo mês", f"Criar lançamentos zerados para {prox_mes}?"):
            return
        backup_database("antes_lancar_proximo_mes")
        criados = 0
        for conta in get_recurring_categories():
            cat = conta["categoria"]
            status = "Débito automático" if conta["tipo"] == "debito automatico" else "Não pago"
            existe = query("SELECT 1 FROM lancamentos WHERE mes=? AND categoria=?", (prox_mes, cat))
            if existe:
                continue
            execute("""
                INSERT INTO lancamentos (mes, categoria, valor, observacao, status_lancamento)
                VALUES (?, ?, 0, ?, ?)
            """, (prox_mes, cat, "Criado automaticamente para o próximo mês", status))
            criados += 1
        self.filter_month_var.set(prox_mes)
        self.insight_month_var.set(prox_mes)
        self.refresh_all()
        messagebox.showinfo("Próximo mês", f"{criados} lançamentos criados para {prox_mes}.")

    def show_payment_context_menu(self, event):
        item = self.pay_tree.identify_row(event.y)
        column = self.pay_tree.identify_column(event.x)
        if not item:
            return
        self.pay_tree.selection_set(item)
        self.payment_context = {"item": item, "column": column}
        self.payment_menu.tk_popup(event.x_root, event.y_root)

    def pay_column_name(self, column_id):
        idx = int(column_id.replace("#", "")) - 1
        cols = ("status", "categoria", "vencimento", "valor", "tipo")
        if 0 <= idx < len(cols):
            return cols[idx]
        return None

    def ensure_payment_record(self, mes, categoria):
        row = query("SELECT valor, status_lancamento, observacao FROM lancamentos WHERE mes=? AND categoria=?", (mes, categoria))
        if row:
            return row[0]
        execute("""
            INSERT INTO lancamentos (mes, categoria, valor, observacao, status_lancamento)
            VALUES (?, ?, 0, '', 'Não pago')
        """, (mes, categoria))
        return (0, "Não pago", "")

    def edit_clicked_payment_cell(self):
        ctx = getattr(self, "payment_context", None)
        if not ctx:
            return
        item = ctx["item"]
        col = self.pay_column_name(ctx["column"])
        if not item or not col:
            return
        values = list(self.pay_tree.item(item, "values"))
        status, categoria, vencimento, valor_txt, tipo = values
        mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")

        if col in ("vencimento", "tipo"):
            messagebox.showinfo("Edição", "Vencimento e tipo são definidos nas regras de contas recorrentes. Edite valor, status ou conta.")
            return

        old_categoria = categoria
        self.ensure_payment_record(mes, old_categoria)

        if col == "valor":
            novo = simpledialog.askstring("Editar valor", f"Novo valor para {categoria}:", initialvalue=valor_txt.replace("R$ ", ""))
            if novo is None:
                return
            valor = parse_valor(novo)
            if valor is None:
                messagebox.showerror("Erro", "Valor inválido.")
                return
            backup_database("antes_editar_valor")
            execute("UPDATE lancamentos SET valor=? WHERE mes=? AND categoria=?", (valor, mes, old_categoria))

        elif col == "status":
            novo = simpledialog.askstring("Editar status", "Digite: Pago, Não pago ou Débito automático", initialvalue=status.replace("⚠ Vencido sem lançamento", "Não pago").replace("⚠ Não pago vencido", "Não pago").replace("Não lançado", "Não pago"))
            if novo is None:
                return
            novo = novo.strip()
            validos = {"Pago": "Pago", "Não pago": "Não pago", "Nao pago": "Não pago", "Débito automático": "Débito automático", "Debito automatico": "Débito automático"}
            if novo not in validos:
                messagebox.showerror("Erro", "Status inválido.")
                return
            backup_database("antes_editar_status")
            execute("UPDATE lancamentos SET status_lancamento=? WHERE mes=? AND categoria=?", (validos[novo], mes, old_categoria))

        elif col == "categoria":
            novo = simpledialog.askstring("Editar conta", "Novo nome da conta/categoria:", initialvalue=categoria)
            if novo is None:
                return
            novo = novo.strip()
            if not novo:
                return
            backup_database("antes_editar_categoria")
            if novo not in CATEGORIAS_PADRAO:
                CATEGORIAS_PADRAO.append(novo)
                CATEGORIAS_PADRAO.sort()
                self.refresh_category_combobox()
            execute("UPDATE lancamentos SET categoria=? WHERE mes=? AND categoria=?", (novo, mes, old_categoria))

        self.refresh_all()

    def delete_payment_record(self):
        item = self.pay_tree.selection()
        if not item:
            return
        values = self.pay_tree.item(item[0], "values")
        categoria = values[1]
        mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")
        existe = query("SELECT 1 FROM lancamentos WHERE mes=? AND categoria=?", (mes, categoria))
        if not existe:
            messagebox.showinfo("Deletar", "Esse item ainda não tem lançamento salvo para deletar.")
            return
        if messagebox.askyesno("Deletar lançamento", f"Deletar {categoria} de {mes}?"):
            backup_database("antes_deletar_controle_pagamentos")
            execute("DELETE FROM lancamentos WHERE mes=? AND categoria=?", (mes, categoria))
            self.refresh_all()

    def sort_pay_tree(self, column):
        reverse = False
        if self.pay_sort_state.get("column") == column:
            reverse = not self.pay_sort_state.get("reverse", False)
        self.pay_sort_state = {"column": column, "reverse": reverse}

        def sort_key(item):
            val = self.pay_tree.set(item, column)
            if column == "valor":
                parsed = parse_valor(val)
                return parsed if parsed is not None else 0
            if column == "vencimento":
                try:
                    return datetime.strptime(val, "%d/%m/%Y")
                except Exception:
                    return datetime.max
            return str(val).lower()

        items = list(self.pay_tree.get_children(""))
        items.sort(key=sort_key, reverse=reverse)
        for index, item in enumerate(items):
            self.pay_tree.move(item, "", index)

    def save_entry(self):
        backup_database("antes_lancamento")
        mes = f"{self.year_var.get()}-{self.month_var.get()}"
        categoria = self.cat_var.get().strip()
        valor = parse_valor(self.value_var.get())
        status = self.status_var.get()
        obs = self.obs_var.get().strip()
        if not categoria:
            messagebox.showerror("Erro", "Informe a categoria.")
            return
        if categoria not in CATEGORIAS_PADRAO:
            CATEGORIAS_PADRAO.append(categoria)
            CATEGORIAS_PADRAO.sort()
            self.refresh_category_combobox()
        if valor is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        existente = query("SELECT valor, observacao FROM lancamentos WHERE mes=? AND categoria=?", (mes, categoria))
        if existente:
            atual, obs_atual = existente[0]
            acao = self.decide_duplicate_action(categoria, atual, valor)
            if acao == "cancelar":
                return
            valor_final = atual + valor if acao == "somar" else valor
            obs_final = obs or obs_atual or ""
            execute("UPDATE lancamentos SET valor=?, observacao=?, status_lancamento=? WHERE mes=? AND categoria=?", (valor_final, obs_final, status, mes, categoria))
        else:
            execute("INSERT INTO lancamentos (mes, categoria, valor, observacao, status_lancamento) VALUES (?, ?, ?, ?, ?)", (mes, categoria, valor, obs, status))
        self.value_var.set("")
        self.obs_var.set("")
        self.filter_month_var.set(mes)
        self.insight_month_var.set(mes)
        self.refresh_all()

    def delete_entry(self):
        backup_database("antes_excluir")
        item = self.tree.selection()
        if not item:
            return
        mes, cat, *_ = self.tree.item(item[0], "values")
        if messagebox.askyesno("Confirmar", f"Excluir {cat} de {mes}?"):
            execute("DELETE FROM lancamentos WHERE mes=? AND categoria=?", (mes, cat))
            self.refresh_all()

    def fill_form_from_selection(self, event=None):
        item = self.tree.selection()
        if not item:
            return
        mes, cat, valor, status, obs = self.tree.item(item[0], "values")
        y, m = mes.split("-")
        self.year_var.set(y); self.month_var.set(m); self.cat_var.set(cat)
        self.value_var.set(valor.replace("R$ ", ""))
        self.status_var.set(status)
        self.obs_var.set(obs)
        self.update_suggestion()

    def fill_payment_from_selection(self, event=None):
        item = self.pay_tree.selection()
        if not item:
            return
        status, cat, vencimento, valor, tipo = self.pay_tree.item(item[0], "values")
        mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")
        y, m = mes.split("-")
        self.year_var.set(y); self.month_var.set(m); self.cat_var.set(cat)
        self.update_suggestion()
        if valor and valor != "R$ 0,00":
            self.value_var.set(valor.replace("R$ ", ""))
        else:
            self.use_suggestion()
            if not self.value_var.get():
                self.value_var.set("0,00")
        self.status_var.set("Débito automático" if status == "Débito automático" else "Pago")
        self.obs_var.set("")

    def refresh_all(self):
        meses = self.months_available()
        self.filter_month_combo["values"] = ["Todos"] + meses
        self.insight_month_combo["values"] = meses
        self.refresh_table()
        self.refresh_payments()
        self.refresh_upcoming()
        self.refresh_cards()
        self.refresh_insights()
        self.refresh_cashflow()
        self.refresh_goals()
        self.update_suggestion()

    def show_upcoming_context_menu(self, event):
        item = self.upcoming_tree.identify_row(event.y)
        if not item:
            return
        self.upcoming_tree.selection_set(item)
        self.upcoming_context = {"item": item}
        self.upcoming_menu.tk_popup(event.x_root, event.y_root)

    def ignore_upcoming_pending(self):
        item = self.upcoming_tree.selection()
        if not item:
            return
        data_txt, categoria, status, valor = self.upcoming_tree.item(item[0], "values")
        try:
            venc = datetime.strptime(data_txt, "%d/%m/%Y").date()
        except Exception:
            return
        mes = f"{venc.year}-{venc.month:02d}"
        if not messagebox.askyesno("Regularizar pendência", f"Ignorar '{categoria}' de {data_txt} na lista de vencidos/próximos?\n\nIsso não altera lançamentos já registrados."):
            return
        backup_database("antes_ignorar_pendencia")
        execute("""
            INSERT OR REPLACE INTO pendencias_ignoradas (mes, categoria, vencimento, motivo)
            VALUES (?, ?, ?, 'regularizado')
        """, (mes, categoria, venc.isoformat()))
        self.refresh_upcoming()

    def select_single_insight_month(self):
        self.insight_all_var.set(False)
        self.insight_start_var.set("")
        self.insight_end_var.set("")
        self.refresh_insights()

    def selected_insight_months(self):
        meses = [m for m, _ in self.monthly_totals()]
        if not meses:
            atual = datetime.now().strftime("%Y-%m")
            return [atual]
        if getattr(self, "insight_all_var", None) and self.insight_all_var.get():
            return meses
        inicio = self.insight_start_var.get().strip()
        fim = self.insight_end_var.get().strip()
        if inicio and fim:
            a, b = sorted([inicio, fim])
            return [m for m in meses if a <= m <= b]
        mes = self.insight_month_var.get().strip()
        return [mes] if mes else [meses[-1]]

    def period_label(self, meses):
        if not meses:
            return "sem período"
        if len(meses) == 1:
            return meses[0]
        return f"{meses[0]} a {meses[-1]}"

    def refresh_upcoming(self):
        if not hasattr(self, "upcoming_tree"):
            return
        for i in self.upcoming_tree.get_children():
            self.upcoming_tree.delete(i)
        hoje = date.today()
        limite = hoje.toordinal() + 7
        itens = []
        meses = {hoje.strftime("%Y-%m")}
        for offset in [-6, -5, -4, -3, -2, -1, 1]:
            ano = hoje.year
            mes_num = hoje.month + offset
            while mes_num <= 0:
                mes_num += 12
                ano -= 1
            while mes_num > 12:
                mes_num -= 12
                ano += 1
            meses.add(f"{ano}-{mes_num:02d}")

        ignoradas = {
            (mes, cat, venc)
            for mes, cat, venc in query("SELECT mes, categoria, vencimento FROM pendencias_ignoradas")
        }

        for mes in meses:
            dados = {cat: (valor, status or "Pago") for cat, valor, status in query("SELECT categoria, valor, status_lancamento FROM lancamentos WHERE mes=?", (mes,))}
            for conta in get_recurring_categories():
                venc = due_date_for_month(mes, conta["dia"])
                if not venc:
                    continue
                cat = conta["categoria"]
                if (mes, cat, venc.isoformat()) in ignoradas:
                    continue
                valor, stat = dados.get(cat, (None, None))
                status = status_pagamento(mes, valor, stat, conta["dia"], conta["tipo"])
                vencido_pendente = venc < hoje and status not in ("Pago", "Débito automático")
                proximos = hoje.toordinal() <= venc.toordinal() <= limite
                if vencido_pendente or proximos:
                    itens.append((venc, cat, status, brl(valor if valor is not None else 0)))
        for venc, cat, status, valor in sorted(itens, key=lambda x: x[0]):
            tag = "ok" if status == "Pago" else "alerta"
            self.upcoming_tree.insert("", "end", values=(venc.strftime("%d/%m/%Y"), cat, status, valor), tags=(tag,))

    def save_income(self):
        backup_database("antes_receita")
        mes = f"{self.rec_year_var.get()}-{self.rec_month_var.get()}"
        desc = self.rec_desc_var.get().strip()
        valor = parse_valor(self.rec_value_var.get())
        obs = self.rec_obs_var.get().strip()
        if not desc:
            messagebox.showerror("Erro", "Informe a descrição da receita.")
            return
        if valor is None:
            messagebox.showerror("Erro", "Valor inválido.")
            return
        execute("INSERT INTO receitas (mes, descricao, valor, observacao) VALUES (?, ?, ?, ?)", (mes, desc, valor, obs))
        self.rec_desc_var.set(""); self.rec_value_var.set(""); self.rec_obs_var.set("")
        self.insight_month_var.set(mes); self.filter_month_var.set(mes)
        self.refresh_all()

    def delete_income(self):
        backup_database("antes_excluir_receita")
        item = self.income_tree.selection()
        if not item:
            return
        rec_id = self.income_tree.item(item[0], "values")[0]
        if messagebox.askyesno("Confirmar", "Excluir receita selecionada?"):
            execute("DELETE FROM receitas WHERE id=?", (rec_id,))
            self.refresh_all()

    def save_goal(self):
        backup_database("antes_meta")
        nome = self.goal_name_var.get().strip()
        alvo = parse_valor(self.goal_target_var.get())
        atual = parse_valor(self.goal_current_var.get())
        obs = self.goal_obs_var.get().strip()
        if not nome:
            messagebox.showerror("Erro", "Informe o nome da meta.")
            return
        if alvo is None or atual is None:
            messagebox.showerror("Erro", "Valores inválidos.")
            return
        item = self.goal_tree.selection()
        if item:
            goal_id = self.goal_tree.item(item[0], "values")[0]
            execute("UPDATE metas SET nome=?, valor_alvo=?, valor_atual=?, observacao=? WHERE id=?", (nome, alvo, atual, obs, goal_id))
        else:
            execute("INSERT INTO metas (nome, valor_alvo, valor_atual, observacao) VALUES (?, ?, ?, ?)", (nome, alvo, atual, obs))
        self.goal_name_var.set(""); self.goal_target_var.set(""); self.goal_current_var.set(""); self.goal_obs_var.set("")
        self.refresh_all()

    def delete_goal(self):
        backup_database("antes_excluir_meta")
        item = self.goal_tree.selection()
        if not item:
            return
        goal_id = self.goal_tree.item(item[0], "values")[0]
        if messagebox.askyesno("Confirmar", "Excluir meta selecionada?"):
            execute("DELETE FROM metas WHERE id=?", (goal_id,))
            self.refresh_all()

    def fill_goal_from_selection(self, event=None):
        item = self.goal_tree.selection()
        if not item:
            return
        goal_id, nome, alvo, atual, progresso, obs = self.goal_tree.item(item[0], "values")
        self.goal_name_var.set(nome)
        self.goal_target_var.set(alvo.replace("R$ ", ""))
        self.goal_current_var.set(atual.replace("R$ ", ""))
        self.goal_obs_var.set(obs)

    def refresh_cashflow(self):
        if not hasattr(self, "income_tree"):
            return
        for i in self.income_tree.get_children():
            self.income_tree.delete(i)
        mes = self.insight_month_var.get() or datetime.now().strftime("%Y-%m")
        rows = query("SELECT id, mes, descricao, valor, observacao FROM receitas ORDER BY mes DESC, id DESC")
        for row in rows:
            self.income_tree.insert("", "end", values=(row[0], row[1], row[2], brl(row[3]), row[4] or ""))
        receitas = query("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE mes=?", (mes,))[0][0]
        despesas = query("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE mes=?", (mes,))[0][0]
        pago, nao_pago, pendente, proj = self.projection_for_month(mes)
        saldo_proj = receitas - proj
        self.cash_receitas_card.value_label.configure(text=brl(receitas))
        self.cash_despesas_card.value_label.configure(text=brl(despesas))
        self.cash_saldo_card.value_label.configure(text=brl(saldo_proj))

    def refresh_goals(self):
        if not hasattr(self, "goal_tree"):
            return
        for i in self.goal_tree.get_children():
            self.goal_tree.delete(i)
        rows = query("SELECT id, nome, valor_alvo, valor_atual, observacao FROM metas ORDER BY id DESC")
        for goal_id, nome, alvo, atual, obs in rows:
            progresso = (atual / alvo * 100) if alvo else 0
            self.goal_tree.insert("", "end", values=(goal_id, nome, brl(alvo), brl(atual), f"{progresso:.1f}%", obs or ""))

    def manual_backup(self):
        destino = backup_database("manual")
        if destino:
            exportado = export_snapshot_csv()
            messagebox.showinfo("Backup", f"Backup criado:\n{destino}\n\nExportação CSV:\n{exportado}")
        else:
            messagebox.showwarning("Backup", "Banco de dados não encontrado.")

    def git_backup_push(self):
        destino = backup_database("git")
        export_snapshot_csv()
        try:
            subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
            commit = subprocess.run(["git", "commit", "-m", "backup"], capture_output=True, text=True)
            if commit.returncode != 0 and "nothing to commit" not in (commit.stdout + commit.stderr).lower():
                raise subprocess.CalledProcessError(commit.returncode, commit.args, output=commit.stdout, stderr=commit.stderr)
            push = subprocess.run(["git", "push"], check=True, capture_output=True, text=True)
            messagebox.showinfo("Git", "Backup/commit enviados para o GitHub.")
        except Exception as e:
            messagebox.showerror("Git", f"Backup local criado, mas o envio para Git falhou.\n\nDetalhe: {e}")

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        mes = self.selected_filter_month()
        if mes:
            rows = query("SELECT mes, categoria, valor, status_lancamento, observacao FROM lancamentos WHERE mes=? ORDER BY valor DESC", (mes,))
        else:
            rows = query("SELECT mes, categoria, valor, status_lancamento, observacao FROM lancamentos ORDER BY mes DESC, valor DESC")
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], brl(row[2]), row[3] or "Pago", row[4] or ""))

    def refresh_payments(self):
        for i in self.pay_tree.get_children():
            self.pay_tree.delete(i)
        mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")
        rows = query("SELECT categoria, valor, status_lancamento FROM lancamentos WHERE mes=?", (mes,))
        dados = {cat: (valor, status or "Pago") for cat, valor, status in rows}
        ordem = {"⚠ Vencido sem lançamento":0, "⚠ Não pago vencido":1, "Não pago":2, "Não lançado":3, "Débito automático":4, "Pago":5}
        linhas = []

        recorrentes = {conta["categoria"] for conta in CONTAS_RECORRENTES}
        for conta in get_recurring_categories():
            cat = conta["categoria"]
            valor, stat = dados.get(cat, (None, None))
            status = status_pagamento(mes, valor, stat, conta["dia"], conta["tipo"])
            venc = due_date_for_month(mes, conta["dia"])
            venc_txt = venc.strftime("%d/%m/%Y") if venc else "Débito automático"
            tipo_txt = "Débito automático" if conta["tipo"] == "debito automatico" else "Manual"
            linhas.append((ordem.get(status, 9), status, cat, venc_txt, brl(valor if valor is not None else 0), tipo_txt))

        # Também mostra categorias extras lançadas naquele mês
        for cat, (valor, stat) in dados.items():
            if cat in recorrentes:
                continue
            status = "Pago" if stat == "Pago" else ("Débito automático" if stat == "Débito automático" else "Não pago")
            linhas.append((ordem.get(status, 9), status, cat, "Sem regra", brl(valor if valor is not None else 0), "Extra"))

        for _, status, cat, venc, valor, tipo in sorted(linhas, key=lambda x: (x[0], x[3], x[2])):
            self.pay_tree.insert("", "end", values=(status, cat, venc, valor, tipo), tags=(status,))

        if getattr(self, "pay_sort_state", {}).get("column"):
            col = self.pay_sort_state["column"]
            current_reverse = self.pay_sort_state.get("reverse", False)
            self.pay_sort_state["reverse"] = not current_reverse
            self.sort_pay_tree(col)

    def monthly_totals(self):
        return query("SELECT mes, SUM(valor) FROM lancamentos GROUP BY mes ORDER BY mes")

    def refresh_cards(self):
        totals = self.monthly_totals()
        if not totals:
            return
        mes = self.selected_filter_month() or totals[-1][0]
        total_mes = query("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE mes=?", (mes,))[0][0]
        media = statistics.mean([x[1] for x in totals])
        maior = query("SELECT categoria, valor FROM lancamentos WHERE mes=? ORDER BY valor DESC LIMIT 1", (mes,))
        self.card_total.value_label.configure(text=f"{mes}: {brl(total_mes)}")
        self.card_media.value_label.configure(text=brl(media))
        self.card_maior.value_label.configure(text=f"{maior[0][0]} • {brl(maior[0][1])}" if maior else "-")

    def clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def refresh_insights(self):
        frames = [self.trend_frame, self.top_frame, self.cards_fixed_frame]
        if hasattr(self, "health_frame"):
            frames.append(self.health_frame)
        for f in frames:
            self.clear_frame(f)
        self.insights_text.delete("1.0", "end")

        meses = self.selected_insight_months()
        all_months = [m for m, _ in self.monthly_totals()]
        if hasattr(self, "insight_month_combo"):
            self.insight_month_combo["values"] = all_months
            self.insight_start_combo["values"] = all_months
            self.insight_end_combo["values"] = all_months

        totals = self.monthly_totals()
        totals_sel = [(m, v) for m, v in totals if m in meses]
        top = self.top_categories_for_months(meses)

        if HAS_MATPLOTLIB:
            self.draw_matplotlib_trend(totals_sel or totals)
            self.draw_matplotlib_top(top)
            self.draw_matplotlib_cards_fixed(meses)
            self.draw_matplotlib_health(meses)
        else:
            self.draw_canvas_message(self.trend_frame, "Instale matplotlib para gráficos melhores: pip install matplotlib")
            self.draw_canvas_top(top)
            self.draw_canvas_cards_fixed(meses)
            self.draw_canvas_health(meses)

        self.update_projection_label_multi(meses)
        self.generate_text_insights_multi(meses, top)

    def top_categories_for_months(self, meses):
        if not meses:
            return []
        placeholders = ",".join("?" for _ in meses)
        return query(f"""
            SELECT categoria, SUM(valor) total
            FROM lancamentos
            WHERE mes IN ({placeholders}) AND valor > 0
            GROUP BY categoria
            ORDER BY total DESC
            LIMIT 10
        """, tuple(meses))

    def draw_matplotlib_trend(self, totals):
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        meses = [x[0] for x in totals]; vals = [x[1] for x in totals]
        ax.plot(meses, vals, marker="o", linewidth=2)
        ax.grid(True, alpha=.25); ax.set_ylabel("R$")
        ax.tick_params(axis="x", rotation=45, labelsize=8); fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.trend_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

    def draw_matplotlib_top(self, top):
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        cats = [x[0] for x in reversed(top)]; vals = [x[1] for x in reversed(top)]
        ax.barh(cats, vals); ax.grid(True, axis="x", alpha=.25); ax.set_xlabel("R$")
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.top_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

    def series_cartoes_fixos(self, meses=None):
        dados = []
        month_list = meses or [m for m, _ in self.monthly_totals()]
        for mes in month_list:
            rows = query("SELECT categoria, valor FROM lancamentos WHERE mes=?", (mes,))
            dados.append((mes, sum(v for c,v in rows if c in CARTOES), sum(v for c,v in rows if c in FIXOS)))
        return dados

    def draw_matplotlib_cards_fixed(self, meses=None):
        dados = self.series_cartoes_fixos(meses)
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        labels = [x[0] for x in dados]
        ax.plot(labels, [x[1] for x in dados], marker="o", linewidth=2, label="Cartões")
        ax.plot(labels, [x[2] for x in dados], marker="o", linewidth=2, label="Fixos")
        ax.grid(True, alpha=.25); ax.legend(); ax.tick_params(axis="x", rotation=45, labelsize=8)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.cards_fixed_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

    def draw_matplotlib_health(self, meses):
        dados = self.health_series(meses)
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        labels = [x["mes"] for x in dados]
        receitas = [x["receitas"] for x in dados]
        despesas = [x["despesas"] for x in dados]
        saldo = [x["saldo"] for x in dados]
        ax.plot(labels, receitas, marker="o", linewidth=2, label="Receitas")
        ax.plot(labels, despesas, marker="o", linewidth=2, label="Despesas")
        ax.bar(labels, saldo, alpha=.35, label="Saldo")
        ax.axhline(0, linewidth=1)
        ax.grid(True, alpha=.25); ax.legend(fontsize=8); ax.tick_params(axis="x", rotation=45, labelsize=8)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.health_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

    def draw_canvas_message(self, frame, text):
        canvas = tk.Canvas(frame, height=140, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(10, 20, text=text, anchor="nw", fill="#6b7280")

    def draw_canvas_top(self, top):
        canvas = tk.Canvas(self.top_frame, height=220, bg="white", highlightthickness=0); canvas.pack(fill="both", expand=True)
        if not top: return
        maxv = max(v for _, v in top) or 1; y = 20
        for cat, val in top:
            canvas.create_text(10, y+10, text=cat[:24], anchor="w")
            canvas.create_rectangle(200, y, 200 + int(350*val/maxv), y+20, fill="#2563eb", outline="")
            canvas.create_text(210 + int(350*val/maxv), y+10, text=brl(val), anchor="w")
            y += 28

    def draw_canvas_cards_fixed(self, meses=None):
        canvas = tk.Canvas(self.cards_fixed_frame, height=160, bg="white", highlightthickness=0); canvas.pack(fill="both", expand=True)
        dados = self.series_cartoes_fixos(meses)
        if not dados: return
        ult = dados[-1]
        canvas.create_text(10, 20, text="Cartões x Fixos", anchor="w", font=("Segoe UI", 11, "bold"))
        canvas.create_text(10, 55, text=f"{ult[0]} | Cartões: {brl(ult[1])} | Fixos: {brl(ult[2])}", anchor="w")

    def draw_canvas_health(self, meses):
        canvas = tk.Canvas(self.health_frame, height=160, bg="white", highlightthickness=0); canvas.pack(fill="both", expand=True)
        dados = self.health_series(meses)
        if not dados: return
        total_receitas = sum(x["receitas"] for x in dados)
        total_despesas = sum(x["despesas"] for x in dados)
        canvas.create_text(10, 20, text="Saúde financeira do período", anchor="w", font=("Segoe UI", 11, "bold"))
        canvas.create_text(10, 55, text=f"Receitas: {brl(total_receitas)} | Despesas: {brl(total_despesas)} | Saldo: {brl(total_receitas-total_despesas)}", anchor="w")

    def health_series(self, meses):
        dados = []
        for mes in meses:
            receitas = query("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE mes=?", (mes,))[0][0]
            despesas = query("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE mes=?", (mes,))[0][0]
            dados.append({"mes": mes, "receitas": receitas, "despesas": despesas, "saldo": receitas - despesas})
        return dados

    def projection_for_month(self, mes):
        rows = query("SELECT categoria, valor, status_lancamento FROM lancamentos WHERE mes=?", (mes,))
        dados = {cat: (valor, status or "Pago") for cat, valor, status in rows}
        pago = sum(v for c,(v,s) in dados.items() if s in ("Pago", "Débito automático"))
        nao_pago = sum(v for c,(v,s) in dados.items() if s == "Não pago")
        pendente = 0
        for conta in get_recurring_categories():
            cat = conta["categoria"]
            if cat not in dados:
                sugestao, _ = self.get_suggested_value(cat)
                pendente += sugestao or 0
        return pago, nao_pago, pendente, pago + nao_pago + pendente

    def update_projection_label_multi(self, meses):
        pago = nao_pago = pendente = proj = 0
        for mes in meses:
            p, n, pe, pr = self.projection_for_month(mes)
            pago += p; nao_pago += n; pendente += pe; proj += pr
        self.proj_label.configure(text=f"{self.period_label(meses)} | Pago: {brl(pago)} | Não pago: {brl(nao_pago)} | Pendente estimado: {brl(pendente)} | Projeção: {brl(proj)}")

    def generate_text_insights_multi(self, meses, top):
        if not meses:
            self.insights_text.insert("end", "Sem dados para analisar.")
            return
        placeholders = ",".join("?" for _ in meses)
        total_despesas = query(f"SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE mes IN ({placeholders})", tuple(meses))[0][0]
        total_receitas = query(f"SELECT COALESCE(SUM(valor),0) FROM receitas WHERE mes IN ({placeholders})", tuple(meses))[0][0]
        saldo = total_receitas - total_despesas
        rows = query(f"SELECT categoria, valor FROM lancamentos WHERE mes IN ({placeholders})", tuple(meses))
        total_cartoes = sum(v for c,v in rows if c in CARTOES)
        total_fixos = sum(v for c,v in rows if c in FIXOS)
        media_mensal = total_despesas / max(1, len(meses))
        taxa_poupanca = (saldo / total_receitas * 100) if total_receitas else 0
        fixos_pct = (total_fixos / total_despesas * 100) if total_despesas else 0
        cartoes_pct = (total_cartoes / total_despesas * 100) if total_despesas else 0

        lines = [
            f"Período analisado: {self.period_label(meses)}.",
            f"Despesas totais: {brl(total_despesas)} | Média mensal: {brl(media_mensal)}.",
            f"Receitas totais: {brl(total_receitas)} | Saldo do período: {brl(saldo)}.",
            "",
            "Leitura de saúde financeira:",
            f"• Taxa de poupança estimada: {taxa_poupanca:.1f}%."
        ]
        if total_receitas:
            if taxa_poupanca >= 20:
                lines.append("  Boa margem: em finanças pessoais, poupar algo próximo de 20% ou mais costuma indicar boa folga para reserva, metas e investimentos.")
            elif taxa_poupanca >= 10:
                lines.append("  Atenção moderada: existe sobra, mas abaixo de uma margem confortável para acelerar reserva e objetivos.")
            else:
                lines.append("  Alerta: a sobra está baixa; vale priorizar redução de despesas variáveis e renegociação de custos fixos.")
        else:
            lines.append("  Cadastre receitas para calcular saldo, taxa de poupança e comprometimento com mais precisão.")

        lines.append(f"• Gastos fixos representam {fixos_pct:.1f}% das despesas.")
        if fixos_pct > 60:
            lines.append("  Alerta: fixos acima de 60% reduzem bastante a flexibilidade mensal.")
        elif fixos_pct > 50:
            lines.append("  Atenção: fixos acima de 50% merecem revisão, especialmente aluguel, escola e parcelas.")
        else:
            lines.append("  Bom sinal: fixos abaixo de 50% deixam mais espaço para decisões e imprevistos.")

        lines.append(f"• Cartões representam {cartoes_pct:.1f}% das despesas.")
        if cartoes_pct > 40:
            lines.append("  Alerta: cartões concentrando mais de 40% das despesas podem esconder consumo variável difícil de controlar.")
        elif cartoes_pct > 25:
            lines.append("  Atenção: cartões estão relevantes; acompanhe semanalmente para evitar surpresa no fechamento.")
        else:
            lines.append("  Cartões parecem sob controle dentro do período analisado.")

        if top:
            lines.append("\nPrincipais gastos do período:")
            for cat, val in top[:6]:
                pct = (val / total_despesas * 100) if total_despesas else 0
                lines.append(f"• {cat}: {brl(val)} ({pct:.1f}%).")

        lines.append("\nSugestões práticas:")
        lines.append("• Revise primeiro cartões e categorias variáveis, pois são as que costumam dar ganho rápido.")
        lines.append("• Use o controle de vencimentos para evitar juros, multa e atrasos.")
        lines.append("• Cadastre receitas para acompanhar saldo real e projeção de caixa.")
        self.insights_text.insert("end", "\n".join(lines))

    def import_csv(self):
        backup_database("antes_importar")
        path = filedialog.askopenfilename(filetypes=[("CSV","*.csv"),("Todos","*.*")])
        if not path: return
        imported = 0
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                valor = parse_valor(row.get("valor", ""))
                if valor is not None:
                    execute("""
                        INSERT OR REPLACE INTO lancamentos (mes,categoria,valor,status_lancamento,observacao)
                        VALUES (?,?,?,?,?)
                    """, (row.get("mes"), row.get("categoria"), valor, row.get("status_lancamento","Pago"), row.get("observacao","")))
                    imported += 1
        self.refresh_all()
        messagebox.showinfo("Importação", f"{imported} lançamentos importados.")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        rows = query("SELECT mes,categoria,valor,status_lancamento,observacao FROM lancamentos ORDER BY mes,categoria")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["mes","categoria","valor","status_lancamento","observacao"])
            writer.writerows(rows)
        messagebox.showinfo("Exportação", "Arquivo exportado com sucesso.")

if __name__ == "__main__":
    init_db()
    backup_database("abertura")
    app = App()
    app.mainloop()
