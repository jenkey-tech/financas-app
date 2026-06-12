
import csv
import sqlite3
import statistics
import calendar
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date

DB_FILE = "financas.db"

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
        return "Não pago vencido"
    return "Não pago"

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

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Finanças Pessoais")
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
        ttk.Button(top, text="Importar CSV", command=self.import_csv).pack(side="right", padx=4)
        ttk.Button(top, text="Exportar CSV", command=self.export_csv).pack(side="right", padx=4)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        self.tab_entries = ttk.Frame(self.notebook, padding=12)
        self.tab_insights = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_entries, text="Lançamentos")
        self.notebook.add(self.tab_insights, text="Insights e gráficos")
        self.create_entries_tab()
        self.create_insights_tab()

    def card(self, parent, title, value):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        lbl = ttk.Label(frame, text=value, style="CardValue.TLabel")
        lbl.pack(anchor="w", pady=(8, 0))
        frame.value_label = lbl
        return frame

    def create_entries_tab(self):
        cards = ttk.Frame(self.tab_entries)
        cards.pack(fill="x", pady=(0, 12))
        self.card_total = self.card(cards, "Total do mês filtrado", "R$ 0,00")
        self.card_media = self.card(cards, "Média mensal geral", "R$ 0,00")
        self.card_maior = self.card(cards, "Maior gasto do mês", "-")
        self.card_total.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.card_media.pack(side="left", fill="x", expand=True, padx=8)
        self.card_maior.pack(side="left", fill="x", expand=True, padx=(8, 0))

        filter_box = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=12)
        filter_box.pack(fill="x", pady=(0, 12))
        ttk.Label(filter_box, text="Visualizar mês", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.filter_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.filter_month_combo = ttk.Combobox(filter_box, textvariable=self.filter_month_var, width=12)
        self.filter_month_combo.grid(row=1, column=0, sticky="w")
        self.filter_month_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_all())
        self.filter_month_combo.bind("<Return>", lambda e: self.refresh_all())
        ttk.Button(filter_box, text="Mês vigente", command=self.current_month).grid(row=1, column=1, padx=8)
        ttk.Button(filter_box, text="Ver todos", command=self.clear_filter).grid(row=1, column=2, padx=8)

        pay_box = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=12)
        pay_box.pack(fill="x", pady=(0, 12))
        ttk.Label(pay_box, text="Controle de pagamentos do mês", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.pay_tree = ttk.Treeview(pay_box, columns=("status", "categoria", "vencimento", "valor", "tipo"), show="headings", height=8)
        for col, label, width in [("status","Status",180),("categoria","Conta",230),("vencimento","Vencimento",120),("valor","Valor",120),("tipo","Tipo",150)]:
            self.pay_tree.heading(col, text=label)
            self.pay_tree.column(col, width=width, anchor="e" if col == "valor" else "w")
        self.pay_tree.tag_configure("Pago", background="#16a34a", foreground="white")
        self.pay_tree.tag_configure("Débito automático", background="#facc15", foreground="#111827")
        self.pay_tree.tag_configure("Não lançado", background="#facc15", foreground="#111827")
        self.pay_tree.tag_configure("⚠ Vencido sem lançamento", background="#f97316", foreground="white")
        self.pay_tree.tag_configure("Não pago", background="#ef4444", foreground="white")
        self.pay_tree.tag_configure("Não pago vencido", background="#b91c1c", foreground="white")
        self.pay_tree.pack(fill="x")
        self.pay_tree.bind("<Double-1>", self.fill_payment_from_selection)

        form = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=12)
        form.pack(fill="x", pady=(0, 12))
        ttk.Label(form, text="Novo/editar lançamento", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=9, sticky="w", pady=(0, 8))
        for i, label in enumerate(["Ano", "Mês", "Categoria", "Valor", "Status", "Obs."]):
            ttk.Label(form, text=label, style="White.TLabel").grid(row=1, column=i, sticky="w")

        today = datetime.now()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=f"{today.month:02d}")
        self.cat_var = tk.StringVar(value=CATEGORIAS_PADRAO[0])
        self.value_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pago")
        self.obs_var = tk.StringVar()
        self.suggestion_var = tk.StringVar(value="Selecione uma categoria para ver sugestão.")

        ttk.Combobox(form, textvariable=self.year_var, values=[str(a) for a in range(2024, today.year+5)], width=8, state="readonly").grid(row=2, column=0, padx=(0,8))
        ttk.Combobox(form, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1,13)], width=6, state="readonly").grid(row=2, column=1, padx=8)
        self.cat_combo = ttk.Combobox(form, textvariable=self.cat_var, values=CATEGORIAS_PADRAO, width=26)
        self.cat_combo.grid(row=2, column=2, padx=8)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.update_suggestion())
        ttk.Entry(form, textvariable=self.value_var, width=14).grid(row=2, column=3, padx=8)
        ttk.Combobox(form, textvariable=self.status_var, values=["Pago", "Não pago", "Débito automático"], width=16, state="readonly").grid(row=2, column=4, padx=8)
        ttk.Entry(form, textvariable=self.obs_var, width=28).grid(row=2, column=5, padx=8)
        ttk.Button(form, text="Salvar", command=self.save_entry).grid(row=2, column=6, padx=6)
        ttk.Button(form, text="Excluir selecionado", command=self.delete_entry).grid(row=2, column=7, padx=6)
        ttk.Label(form, textvariable=self.suggestion_var, style="White.TLabel").grid(row=3, column=0, columnspan=5, sticky="w", pady=(10, 0))
        ttk.Button(form, text="Usar sugestão", command=self.use_suggestion).grid(row=3, column=5, padx=6, pady=(10, 0), sticky="w")

        table_box = ttk.Frame(self.tab_entries, style="Card.TFrame", padding=12)
        table_box.pack(fill="both", expand=True)
        ttk.Label(table_box, text="Lançamentos", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.tree = ttk.Treeview(table_box, columns=("mes","categoria","valor","status","obs"), show="headings")
        for col, label, width in [("mes","Mês",90),("categoria","Categoria",230),("valor","Valor",120),("status","Status",130),("obs","Obs.",240)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="e" if col=="valor" else "w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.fill_form_from_selection)

    def create_insights_tab(self):
        top = ttk.Frame(self.tab_insights, style="Card.TFrame", padding=12)
        top.pack(fill="x", pady=(0, 12))
        ttk.Label(top, text="Mês analisado", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0,8))
        self.insight_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.insight_month_combo = ttk.Combobox(top, textvariable=self.insight_month_var, width=12)
        self.insight_month_combo.grid(row=1, column=0)
        self.insight_month_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_insights())
        self.proj_label = ttk.Label(top, text="", style="White.TLabel")
        self.proj_label.grid(row=1, column=1, sticky="w", padx=18)

        body = ttk.Frame(self.tab_insights)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0,12))
        right = ttk.Frame(body, width=380)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        for title, attr in [("Evolução do total mensal","trend_frame"),("Top gastos do mês","top_frame"),("Cartões x gastos fixos","cards_fixed_frame")]:
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

    def save_entry(self):
        mes = f"{self.year_var.get()}-{self.month_var.get()}"
        categoria = self.cat_var.get().strip()
        valor = parse_valor(self.value_var.get())
        status = self.status_var.get()
        obs = self.obs_var.get().strip()
        if not categoria:
            messagebox.showerror("Erro", "Informe a categoria.")
            return
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
        self.refresh_cards()
        self.refresh_insights()
        self.update_suggestion()

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
        ordem = {"⚠ Vencido sem lançamento":0, "Não pago vencido":1, "Não pago":2, "Não lançado":3, "Débito automático":4, "Pago":5}
        linhas = []
        for conta in CONTAS_RECORRENTES:
            cat = conta["categoria"]
            valor, stat = dados.get(cat, (None, None))
            status = status_pagamento(mes, valor, stat, conta["dia"], conta["tipo"])
            venc = due_date_for_month(mes, conta["dia"])
            venc_txt = venc.strftime("%d/%m/%Y") if venc else "Débito automático"
            tipo_txt = "Débito automático" if conta["tipo"] == "debito automatico" else "Manual"
            linhas.append((ordem.get(status, 9), status, cat, venc_txt, brl(valor if valor is not None else 0), tipo_txt))
        for _, status, cat, venc, valor, tipo in sorted(linhas, key=lambda x: (x[0], x[3], x[2])):
            self.pay_tree.insert("", "end", values=(status, cat, venc, valor, tipo), tags=(status,))

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
        for f in [self.trend_frame, self.top_frame, self.cards_fixed_frame]:
            self.clear_frame(f)
        self.insights_text.delete("1.0", "end")
        mes = self.insight_month_var.get() or datetime.now().strftime("%Y-%m")
        totals = self.monthly_totals()
        top = query("SELECT categoria, valor FROM lancamentos WHERE mes=? AND valor > 0 ORDER BY valor DESC LIMIT 8", (mes,))
        if HAS_MATPLOTLIB:
            self.draw_matplotlib_trend(totals)
            self.draw_matplotlib_top(top)
            self.draw_matplotlib_cards_fixed()
        else:
            self.draw_canvas_message(self.trend_frame, "Instale matplotlib para gráficos melhores: pip install matplotlib")
            self.draw_canvas_top(top)
            self.draw_canvas_cards_fixed()
        self.update_projection_label(mes)
        self.generate_text_insights(mes, totals, top)

    def draw_matplotlib_trend(self, totals):
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        meses = [x[0] for x in totals]; vals = [x[1] for x in totals]
        ax.plot(meses, vals, marker="o", linewidth=2); ax.grid(True, alpha=.25); ax.set_ylabel("R$")
        ax.tick_params(axis="x", rotation=45, labelsize=8); fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.trend_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

    def draw_matplotlib_top(self, top):
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        cats = [x[0] for x in reversed(top)]; vals = [x[1] for x in reversed(top)]
        ax.barh(cats, vals); ax.grid(True, axis="x", alpha=.25); ax.set_xlabel("R$"); fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.top_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

    def series_cartoes_fixos(self):
        dados = []
        for mes, _ in self.monthly_totals():
            rows = query("SELECT categoria, valor FROM lancamentos WHERE mes=?", (mes,))
            dados.append((mes, sum(v for c,v in rows if c in CARTOES), sum(v for c,v in rows if c in FIXOS)))
        return dados

    def draw_matplotlib_cards_fixed(self):
        dados = self.series_cartoes_fixos()
        fig = Figure(figsize=(7, 2.2), dpi=100); ax = fig.add_subplot(111)
        meses = [x[0] for x in dados]
        ax.plot(meses, [x[1] for x in dados], marker="o", linewidth=2, label="Cartões")
        ax.plot(meses, [x[2] for x in dados], marker="o", linewidth=2, label="Fixos")
        ax.grid(True, alpha=.25); ax.legend(); ax.tick_params(axis="x", rotation=45, labelsize=8); fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.cards_fixed_frame); c.draw(); c.get_tk_widget().pack(fill="both", expand=True)

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

    def draw_canvas_cards_fixed(self):
        canvas = tk.Canvas(self.cards_fixed_frame, height=160, bg="white", highlightthickness=0); canvas.pack(fill="both", expand=True)
        dados = self.series_cartoes_fixos()
        if not dados: return
        ult = dados[-1]
        canvas.create_text(10, 20, text="Cartões x Fixos", anchor="w", font=("Segoe UI", 11, "bold"))
        canvas.create_text(10, 55, text=f"{ult[0]} | Cartões: {brl(ult[1])} | Fixos: {brl(ult[2])}", anchor="w")

    def projection_for_month(self, mes):
        rows = query("SELECT categoria, valor, status_lancamento FROM lancamentos WHERE mes=?", (mes,))
        dados = {cat: (valor, status or "Pago") for cat, valor, status in rows}
        pago = sum(v for c,(v,s) in dados.items() if s in ("Pago", "Débito automático"))
        nao_pago = sum(v for c,(v,s) in dados.items() if s == "Não pago")
        pendente = 0
        for conta in CONTAS_RECORRENTES:
            cat = conta["categoria"]
            if cat not in dados:
                sugestao, _ = self.get_suggested_value(cat)
                pendente += sugestao or 0
        return pago, nao_pago, pendente, pago + nao_pago + pendente

    def update_projection_label(self, mes):
        pago, nao_pago, pendente, proj = self.projection_for_month(mes)
        self.proj_label.configure(text=f"Pago: {brl(pago)} | Não pago: {brl(nao_pago)} | Pendente estimado: {brl(pendente)} | Projeção: {brl(proj)}")

    def generate_text_insights(self, mes, totals, top):
        total_mes = query("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE mes=?", (mes,))[0][0]
        pago, nao_pago, pendente, proj = self.projection_for_month(mes)
        lines = [
            f"Total lançado de {mes}: {brl(total_mes)}.",
            f"Pago: {brl(pago)} | Não pago: {brl(nao_pago)} | Pendente estimado: {brl(pendente)}.",
            f"Projeção final do mês: {brl(proj)}."
        ]
        if top:
            lines.append("\nPrincipais gastos:")
            for cat, val in top[:5]:
                pct = (val / total_mes * 100) if total_mes else 0
                lines.append(f"• {cat}: {brl(val)} ({pct:.1f}%).")
        rows = query("SELECT categoria, valor FROM lancamentos WHERE mes=?", (mes,))
        total_cartoes = sum(v for c,v in rows if c in CARTOES)
        total_fixos = sum(v for c,v in rows if c in FIXOS)
        lines.append("\nComposição:")
        lines.append(f"• Cartões: {brl(total_cartoes)}.")
        lines.append(f"• Fixos: {brl(total_fixos)}.")
        lines.append("\nDica: use o painel de pagamentos como checklist mensal; o que ficar laranja/vermelho precisa de ação.")
        self.insights_text.insert("end", "\n".join(lines))

    def import_csv(self):
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
    app = App()
    app.mainloop()
