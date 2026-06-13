"""Interface gráfica principal."""

import csv
import statistics
import subprocess
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, date

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False

from config import APP_VERSION, DB_FILE, BACKUP_DIR, CATEGORIAS_PADRAO, CATEGORIAS_ACUMULATIVAS, CATEGORIAS_FIXAS, CARTOES, FIXOS, CONTAS_RECORRENTES
from db import (
    init_db,
    query,
    execute,
    backup_database,
    export_snapshot_csv,
    get_categories,
    get_category_names,
    get_recurring_categories,
    upsert_category,
)
from utils import brl, parse_valor, due_date_for_month, status_pagamento

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
        style.configure("CompactCard.TFrame", background="white")
        style.configure("CompactTitle.TLabel", font=("Segoe UI", 8), background="white", foreground="#6b7280")
        style.configure("CompactValue.TLabel", font=("Segoe UI", 12, "bold"), background="white", foreground="#111827")
        style.configure("CompactValueGreen.TLabel", font=("Segoe UI", 12, "bold"), background="white", foreground="#16a34a")
        style.configure("CompactValueRed.TLabel", font=("Segoe UI", 12, "bold"), background="white", foreground="#dc2626")
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 6))
        style.configure("Secondary.TButton", font=("Segoe UI", 9), padding=(10, 6))
        style.configure("Danger.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 6))

    def create_layout(self):
        top = ttk.Frame(self, padding=18)
        top.pack(fill="x")
        ttk.Label(top, text="Painel de Finanças", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Commit estado atual", command=self.commit_current_state, style="Primary.TButton").pack(side="right", padx=4)
        ttk.Button(top, text="Restaurar anterior", command=self.restore_previous_state, style="Secondary.TButton").pack(side="right", padx=4)
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

    def compact_card(self, parent, title, value):
        frame = ttk.Frame(parent, style="CompactCard.TFrame", padding=(10, 8))
        ttk.Label(frame, text=title, style="CompactTitle.TLabel").pack(anchor="w")
        lbl = ttk.Label(frame, text=value, style="CompactValue.TLabel")
        lbl.pack(anchor="w", pady=(2, 0))
        frame.value_label = lbl
        return frame

    def create_entries_tab(self):
        # Linha 1: indicadores compactos
        cards = ttk.Frame(self.tab_entries)
        cards.pack(fill="x", pady=(0, 8))
        self.card_total = self.compact_card(cards, "Total do mês", "R$ 0,00")
        self.card_paid = self.compact_card(cards, "Já pago", "R$ 0,00")
        self.card_unpaid = self.compact_card(cards, "Falta pagar", "R$ 0,00")
        self.card_paid.value_label.configure(style="CompactValueGreen.TLabel")
        self.card_unpaid.value_label.configure(style="CompactValueRed.TLabel")
        self.card_total.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.card_paid.pack(side="left", fill="x", expand=True, padx=6)
        self.card_unpaid.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # Linha 2: filtro e lançamento lado a lado
        top_grid = ttk.Frame(self.tab_entries)
        top_grid.pack(fill="x", pady=(0, 8))

        filter_box = ttk.Frame(top_grid, style="Card.TFrame", padding=10)
        filter_box.pack(side="left", fill="y", padx=(0, 8))
        ttk.Label(filter_box, text="Mês", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        self.filter_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.filter_month_combo = ttk.Combobox(filter_box, textvariable=self.filter_month_var, width=12)
        self.filter_month_combo.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.filter_month_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_all())
        self.filter_month_combo.bind("<Return>", lambda e: self.refresh_all())
        ttk.Button(filter_box, text="Mês vigente", command=self.current_month, style="Secondary.TButton").grid(row=2, column=0, sticky="ew", pady=(8, 0), padx=(0, 3))
        ttk.Button(filter_box, text="+ Próximo mês", command=self.launch_next_month, style="Primary.TButton").grid(row=2, column=1, sticky="ew", pady=(8, 0), padx=(3, 0))

        form = ttk.Frame(top_grid, style="Card.TFrame", padding=10)
        form.pack(side="left", fill="both", expand=True)
        ttk.Label(form, text="Novo/editar lançamento", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))
        ttk.Button(form, text="⚙ Gerenciar categorias", command=self.open_category_manager, style="Secondary.TButton").grid(row=0, column=6, columnspan=2, sticky="e", padx=6)

        today = datetime.now()
        self.year_var = tk.StringVar(value=str(today.year))
        self.month_var = tk.StringVar(value=f"{today.month:02d}")
        self.cat_var = tk.StringVar(value=CATEGORIAS_PADRAO[0])
        self.value_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Pago")
        self.obs_var = tk.StringVar()
        self.suggestion_var = tk.StringVar(value="Selecione uma categoria para ver sugestão.")

        fields = [
            ("Ano", 0), ("Mês", 1), ("Categoria", 2), ("Valor", 3), ("Status", 4), ("Obs.", 5)
        ]
        for label, col in fields:
            ttk.Label(form, text=label, style="White.TLabel").grid(row=1, column=col, sticky="w")

        ttk.Combobox(form, textvariable=self.year_var, values=[str(a) for a in range(2024, today.year+5)], width=7, state="readonly").grid(row=2, column=0, padx=(0,6), sticky="w")
        ttk.Combobox(form, textvariable=self.month_var, values=[f"{m:02d}" for m in range(1,13)], width=5, state="readonly").grid(row=2, column=1, padx=6, sticky="w")
        self.cat_combo = ttk.Combobox(form, textvariable=self.cat_var, values=get_category_names(), width=24)
        self.cat_combo.grid(row=2, column=2, padx=6, sticky="ew")
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.update_suggestion())
        self.cat_combo.bind("<KeyRelease>", lambda e: self.update_suggestion())
        ttk.Entry(form, textvariable=self.value_var, width=12).grid(row=2, column=3, padx=6, sticky="w")
        ttk.Combobox(form, textvariable=self.status_var, values=["Pago", "Não pago", "Débito automático"], width=15, state="readonly").grid(row=2, column=4, padx=6, sticky="w")
        ttk.Entry(form, textvariable=self.obs_var, width=24).grid(row=2, column=5, padx=6, sticky="ew")
        form.columnconfigure(2, weight=1)
        form.columnconfigure(5, weight=1)

        actions = ttk.Frame(form, style="Card.TFrame")
        actions.grid(row=2, column=6, columnspan=2, sticky="e", padx=(8, 0))
        ttk.Button(actions, text="Salvar", command=self.save_entry, style="Primary.TButton").pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Sugestão", command=self.use_suggestion, style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(actions, text="Excluir", command=self.delete_entry, style="Danger.TButton").pack(side="left", padx=(5, 0))

        ttk.Label(form, textvariable=self.suggestion_var, style="White.TLabel").grid(row=3, column=0, columnspan=8, sticky="w", pady=(8, 0))

        # Linha 3: controle de pagamentos + vencidos lado a lado
        middle = ttk.Frame(self.tab_entries)
        middle.pack(fill="both", expand=True, pady=(0, 8))

        pay_box = ttk.Frame(middle, style="Card.TFrame", padding=10)
        pay_box.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ttk.Label(pay_box, text="Controle de pagamentos do mês", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 8))

        pay_container = ttk.Frame(pay_box, style="Card.TFrame")
        pay_container.pack(fill="both", expand=True)
        self.pay_tree = ttk.Treeview(pay_container, columns=("status", "categoria", "vencimento", "valor", "tipo"), show="headings", height=11)
        pay_scroll = ttk.Scrollbar(pay_container, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=pay_scroll.set)
        self.pay_tree.pack(side="left", fill="both", expand=True)
        pay_scroll.pack(side="right", fill="y")

        self.pay_sort_state = {"column": None, "reverse": False}
        for col, label, width in [("status","Status",175),("categoria","Conta",220),("vencimento","Venc.",95),("valor","Valor",115),("tipo","Tipo",130)]:
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

        upcoming_box = ttk.Frame(middle, style="Card.TFrame", padding=10)
        upcoming_box.pack(side="right", fill="both", padx=(0, 0))
        ttk.Label(upcoming_box, text="Próximos gastos", style="CardTitle.TLabel").pack(anchor="w", pady=(0, 2))
        self.upcoming_total_label = ttk.Label(upcoming_box, text="Em aberto: R$ 0,00", style="CompactValueRed.TLabel")
        self.upcoming_total_label.pack(anchor="w", pady=(0, 8))
        self.upcoming_tree = ttk.Treeview(upcoming_box, columns=("data", "conta", "status", "valor"), show="headings", height=11)
        upcoming_scroll = ttk.Scrollbar(upcoming_box, orient="vertical", command=self.upcoming_tree.yview)
        self.upcoming_tree.configure(yscrollcommand=upcoming_scroll.set)
        for col, label, width in [("data", "Data", 88), ("conta", "Conta", 180), ("status", "Status", 170), ("valor", "Valor", 105)]:
            self.upcoming_tree.heading(col, text=label)
            self.upcoming_tree.column(col, width=width, anchor="e" if col == "valor" else "w")
        self.upcoming_tree.tag_configure("alerta", background="#f97316", foreground="white")
        self.upcoming_tree.tag_configure("ok", background="#dcfce7", foreground="#111827")
        self.upcoming_tree.pack(side="left", fill="both", expand=True)
        upcoming_scroll.pack(side="right", fill="y")
        self.upcoming_tree.bind("<Button-3>", self.show_upcoming_context_menu)
        self.upcoming_menu = tk.Menu(self, tearoff=0)
        self.upcoming_menu.add_command(label="Regularizar/ignorar pendência", command=self.ignore_upcoming_pending)

        # Tabela inferior de lançamentos removida da interface.
        # A edição principal passa a ser feita pelo controle de pagamentos e pelo formulário acima.
        self.tree = None

    def create_insights_tab(self):
        top = ttk.Frame(self.tab_insights, style="Card.TFrame", padding=10)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Período analisado", style="CardTitle.TLabel").grid(row=0, column=0, columnspan=7, sticky="w", pady=(0,6))

        self.insight_month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.insight_start_var = tk.StringVar(value="")
        self.insight_end_var = tk.StringVar(value="")
        self.insight_all_var = tk.BooleanVar(value=False)
        self.insight_category_var = tk.StringVar(value="Todas")

        labels = [("Mês", 0), ("De", 1), ("Até", 2), ("Categoria", 5)]
        for text, col in labels:
            ttk.Label(top, text=text, style="White.TLabel").grid(row=1, column=col, sticky="w", padx=(10 if col else 0, 0))

        self.insight_month_combo = ttk.Combobox(top, textvariable=self.insight_month_var, width=12)
        self.insight_month_combo.grid(row=2, column=0, sticky="w")
        self.insight_month_combo.bind("<<ComboboxSelected>>", lambda e: self.select_single_insight_month())

        self.insight_start_combo = ttk.Combobox(top, textvariable=self.insight_start_var, width=12)
        self.insight_start_combo.grid(row=2, column=1, sticky="w", padx=(10, 0))
        self.insight_start_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_insights())

        self.insight_end_combo = ttk.Combobox(top, textvariable=self.insight_end_var, width=12)
        self.insight_end_combo.grid(row=2, column=2, sticky="w", padx=(10, 0))
        self.insight_end_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_insights())

        ttk.Checkbutton(top, text="Ver todos", variable=self.insight_all_var, command=self.refresh_insights).grid(row=2, column=3, sticky="w", padx=12)
        ttk.Button(top, text="Aplicar", command=self.refresh_insights, style="Primary.TButton").grid(row=2, column=4, sticky="w", padx=4)

        self.insight_category_combo = ttk.Combobox(top, textvariable=self.insight_category_var, width=22, state="readonly")
        self.insight_category_combo.grid(row=2, column=5, sticky="w", padx=(10, 0))
        self.insight_category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_insights())

        ttk.Button(top, text="Detalhar análise", command=self.show_detailed_insights, style="Secondary.TButton").grid(row=2, column=6, sticky="w", padx=8)

        self.proj_label = ttk.Label(top, text="", style="White.TLabel")
        self.proj_label.grid(row=3, column=0, columnspan=7, sticky="w", pady=(8, 0))

        body = ttk.Frame(self.tab_insights)
        body.pack(fill="both", expand=True)

        charts_area = ttk.Frame(body)
        charts_area.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = ttk.Frame(body, width=360)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        upper = ttk.Frame(charts_area)
        upper.pack(fill="both", expand=True, pady=(0, 8))
        lower = ttk.Frame(charts_area)
        lower.pack(fill="both", expand=True)

        trend_card = ttk.Frame(upper, style="Card.TFrame", padding=10)
        trend_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ttk.Label(trend_card, text="Evolução dos gastos", style="CardTitle.TLabel").pack(anchor="w")
        self.trend_frame = ttk.Frame(trend_card, style="Card.TFrame")
        self.trend_frame.pack(fill="both", expand=True, pady=(6, 0))

        top_card = ttk.Frame(upper, style="Card.TFrame", padding=10)
        top_card.pack(side="left", fill="both", expand=True)
        ttk.Label(top_card, text="Top gastos do período", style="CardTitle.TLabel").pack(anchor="w")
        self.top_frame = ttk.Frame(top_card, style="Card.TFrame")
        self.top_frame.pack(fill="both", expand=True, pady=(6, 0))

        health_card = ttk.Frame(lower, style="Card.TFrame", padding=10)
        health_card.pack(fill="both", expand=True)
        ttk.Label(health_card, text="Saúde financeira", style="CardTitle.TLabel").pack(anchor="w")
        self.health_frame = ttk.Frame(health_card, style="Card.TFrame")
        self.health_frame.pack(fill="both", expand=True, pady=(6, 0))

        txt_card = ttk.Frame(right, style="Card.TFrame", padding=10)
        txt_card.pack(fill="both", expand=True)
        ttk.Label(txt_card, text="Resumo", style="CardTitle.TLabel").pack(anchor="w")
        self.insights_text = tk.Text(txt_card, wrap="word", bg="white", relief="flat", font=("Segoe UI", 10), height=12)
        self.insights_text.pack(fill="both", expand=True, pady=(6,0))

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
        mes = f"{self.year_var.get()}-{self.month_var.get()}"
        cat = self.cat_var.get().strip()
        if not cat:
            return
        existe = query("SELECT 1 FROM lancamentos WHERE mes=? AND categoria=?", (mes, cat))
        if not existe:
            messagebox.showinfo("Excluir", "Não existe lançamento salvo para esta categoria neste mês.")
            return
        if messagebox.askyesno("Confirmar", f"Excluir {cat} de {mes}?"):
            execute("DELETE FROM lancamentos WHERE mes=? AND categoria=?", (mes, cat))
            self.refresh_all()

    def fill_form_from_selection(self, event=None):
        if not hasattr(self, "tree") or self.tree is None:
            return
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
        total_em_aberto = 0
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
                    valor_num = valor if valor is not None else 0
                    if status not in ("Pago", "Débito automático"):
                        total_em_aberto += valor_num
                    itens.append((venc, cat, status, brl(valor_num)))
        for venc, cat, status, valor in sorted(itens, key=lambda x: x[0]):
            tag = "ok" if status == "Pago" else "alerta"
            self.upcoming_tree.insert("", "end", values=(venc.strftime("%d/%m/%Y"), cat, status, valor), tags=(tag,))
        if hasattr(self, "upcoming_total_label"):
            self.upcoming_total_label.configure(text=f"Em aberto: {brl(total_em_aberto)}")

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

    def previous_state_path(self):
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        return Path(BACKUP_DIR) / "estado_anterior.db"

    def commit_current_state(self):
        """Salva somente o último estado anterior e cria commit local."""
        try:
            db_origem = Path(DB_FILE)
            if db_origem.exists():
                shutil.copy2(db_origem, self.previous_state_path())

            exportado = export_snapshot_csv()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
            commit = subprocess.run(
                ["git", "commit", "-m", f"dados {timestamp}"],
                capture_output=True,
                text=True
            )
            saida = (commit.stdout + commit.stderr).strip()
            if commit.returncode != 0:
                if "nothing to commit" in saida.lower() or "nada a submeter" in saida.lower():
                    messagebox.showinfo("Git", f"Nenhuma alteração nova para commitar.\n\nEstado anterior salvo em:\n{self.previous_state_path()}\n\nSnapshot:\n{exportado}")
                    return
                raise subprocess.CalledProcessError(commit.returncode, commit.args, output=commit.stdout, stderr=commit.stderr)
            messagebox.showinfo(
                "Git",
                f"Commit local criado.\n\nEstado anterior salvo em:\n{self.previous_state_path()}\n\nSnapshot:\n{exportado}\n\nPara enviar ao GitHub: git push"
            )
        except FileNotFoundError:
            messagebox.showerror("Git", "Git não encontrado. Verifique se o Git está instalado e disponível no PATH.")
        except Exception as e:
            messagebox.showerror("Git", f"Não foi possível criar o commit local.\n\nDetalhe: {e}")

    def restore_previous_state(self):
        origem = self.previous_state_path()
        if not origem.exists():
            messagebox.showwarning("Restaurar", "Nenhum estado anterior salvo ainda.")
            return
        if not messagebox.askyesno("Restaurar estado anterior", "Restaurar o banco para o último estado anterior salvo?\n\nIsso substituirá o financas.db atual."):
            return
        try:
            backup_database("antes_restaurar_estado")
            shutil.copy2(origem, DB_FILE)
            self.refresh_all()
            if hasattr(self, "refresh_cashflow"):
                self.refresh_cashflow()
            if hasattr(self, "refresh_goals"):
                self.refresh_goals()
            messagebox.showinfo("Restaurar", "Estado anterior restaurado com sucesso.")
        except Exception as e:
            messagebox.showerror("Restaurar", f"Não foi possível restaurar.\n\nDetalhe: {e}")

    def refresh_table(self):
        if not hasattr(self, "tree") or self.tree is None:
            return
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

        recorrentes = {conta["categoria"] for conta in get_recurring_categories()}
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
        mes = self.selected_filter_month() or datetime.now().strftime("%Y-%m")
        total_mes = query("SELECT COALESCE(SUM(valor),0) FROM lancamentos WHERE mes=?", (mes,))[0][0]
        rows = query("SELECT valor, status_lancamento FROM lancamentos WHERE mes=?", (mes,))
        pago = sum(valor for valor, status in rows if (status or "Pago") in ("Pago", "Débito automático"))
        falta = sum(valor for valor, status in rows if (status or "Pago") == "Não pago")
        self.card_total.value_label.configure(text=f"{mes}: {brl(total_mes)}")
        self.card_paid.value_label.configure(text=brl(pago))
        self.card_unpaid.value_label.configure(text=brl(falta))

    def clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def refresh_insights(self):
        frames = [self.trend_frame, self.top_frame, self.health_frame]
        for f in frames:
            self.clear_frame(f)
        self.insights_text.delete("1.0", "end")

        meses = self.selected_insight_months()
        all_months = [m for m, _ in self.monthly_totals()]
        if hasattr(self, "insight_month_combo"):
            self.insight_month_combo["values"] = all_months
            self.insight_start_combo["values"] = all_months
            self.insight_end_combo["values"] = all_months
            categorias = ["Todas", "Cartões"] + [c for c in get_category_names() if c not in CARTOES]
            self.insight_category_combo["values"] = categorias
            if self.insight_category_var.get() not in categorias:
                self.insight_category_var.set("Todas")

        categoria = self.insight_category_var.get() if hasattr(self, "insight_category_var") else "Todas"
        trend = self.trend_for_months(meses, categoria)
        top = self.top_categories_for_months(meses, categoria)

        if HAS_MATPLOTLIB:
            self.draw_matplotlib_trend(trend, categoria)
            self.draw_matplotlib_top_pie(top)
            self.draw_matplotlib_health(meses)
        else:
            self.draw_canvas_message(self.trend_frame, "Instale matplotlib para gráficos melhores: pip install matplotlib")
            self.draw_canvas_top(top)
            self.draw_canvas_health(meses)

        self.update_projection_label_multi(meses)
        self.generate_text_insights_multi(meses, top, detailed=False)

    def normalize_chart_category(self, categoria):
        return "Cartões" if categoria in CARTOES else categoria

    def lancamentos_periodo(self, meses):
        if not meses:
            return []
        placeholders = ",".join("?" for _ in meses)
        return query(f"""
            SELECT mes, categoria, valor
            FROM lancamentos
            WHERE mes IN ({placeholders}) AND valor > 0
        """, tuple(meses))

    def trend_for_months(self, meses, categoria="Todas"):
        dados = []
        for mes in meses:
            rows = query("SELECT categoria, valor FROM lancamentos WHERE mes=? AND valor > 0", (mes,))
            if categoria == "Todas":
                total = sum(v for _, v in rows)
            elif categoria == "Cartões":
                total = sum(v for c, v in rows if c in CARTOES)
            else:
                total = sum(v for c, v in rows if c == categoria)
            dados.append((mes, total))
        return dados

    def top_categories_for_months(self, meses, categoria="Todas"):
        acumulado = {}
        for mes, cat, val in self.lancamentos_periodo(meses):
            grupo = self.normalize_chart_category(cat)
            if categoria not in ("Todas", ""):
                if categoria == "Cartões":
                    if cat not in CARTOES:
                        continue
                    grupo = "Cartões"
                elif cat != categoria:
                    continue
            acumulado[grupo] = acumulado.get(grupo, 0) + val
        return sorted(acumulado.items(), key=lambda x: x[1], reverse=True)[:8]

    def draw_matplotlib_trend(self, totals, categoria="Todas"):
        fig = Figure(figsize=(5.6, 2.7), dpi=100)
        ax = fig.add_subplot(111)
        meses = [x[0] for x in totals]
        vals = [x[1] for x in totals]
        ax.plot(meses, vals, marker="o", linewidth=2)
        ax.set_title("Todos os gastos" if categoria == "Todas" else categoria, fontsize=9)
        ax.grid(True, alpha=.25)
        ax.set_ylabel("R$")
        ax.tick_params(axis="x", rotation=35, labelsize=8)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.trend_frame)
        c.draw()
        c.get_tk_widget().pack(fill="both", expand=True)

    def draw_matplotlib_top_pie(self, top):
        fig = Figure(figsize=(5.0, 2.7), dpi=100)
        ax = fig.add_subplot(111)
        if not top:
            ax.text(0.5, 0.5, "Sem dados", ha="center", va="center")
            ax.axis("off")
        else:
            labels = [x[0] for x in top]
            vals = [x[1] for x in top]
            ax.pie(vals, labels=labels, autopct="%1.0f%%", textprops={"fontsize": 7}, startangle=90)
            ax.axis("equal")
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.top_frame)
        c.draw()
        c.get_tk_widget().pack(fill="both", expand=True)

    def draw_matplotlib_health(self, meses):
        dados = self.health_series(meses)
        fig = Figure(figsize=(10.5, 2.4), dpi=100)
        ax = fig.add_subplot(111)
        labels = [x["mes"] for x in dados]
        receitas = [x["receitas"] for x in dados]
        despesas = [x["despesas"] for x in dados]
        saldo = [x["saldo"] for x in dados]
        ax.plot(labels, receitas, marker="o", linewidth=2, label="Receitas")
        ax.plot(labels, despesas, marker="o", linewidth=2, label="Despesas")
        ax.bar(labels, saldo, alpha=.35, label="Saldo")
        ax.axhline(0, linewidth=1)
        ax.grid(True, alpha=.25)
        ax.legend(fontsize=8, loc="best")
        ax.tick_params(axis="x", rotation=35, labelsize=8)
        fig.tight_layout()
        c = FigureCanvasTkAgg(fig, master=self.health_frame)
        c.draw()
        c.get_tk_widget().pack(fill="both", expand=True)

    def draw_canvas_message(self, frame, text):
        canvas = tk.Canvas(frame, height=140, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_text(10, 20, text=text, anchor="nw", fill="#6b7280")

    def draw_canvas_top(self, top):
        canvas = tk.Canvas(self.top_frame, height=220, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        if not top:
            return
        total = sum(v for _, v in top) or 1
        y = 20
        for cat, val in top[:6]:
            pct = val / total * 100
            canvas.create_text(10, y, text=f"{cat}: {pct:.0f}% ({brl(val)})", anchor="w")
            y += 24

    def draw_canvas_health(self, meses):
        canvas = tk.Canvas(self.health_frame, height=150, bg="white", highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        dados = self.health_series(meses)
        total_receitas = sum(x["receitas"] for x in dados)
        total_despesas = sum(x["despesas"] for x in dados)
        canvas.create_text(10, 20, text="Saúde financeira", anchor="w", font=("Segoe UI", 11, "bold"))
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

    def calculate_insights_metrics(self, meses, top):
        if not meses:
            return {}
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
        return {
            "total_despesas": total_despesas,
            "total_receitas": total_receitas,
            "saldo": saldo,
            "total_cartoes": total_cartoes,
            "total_fixos": total_fixos,
            "media_mensal": media_mensal,
            "taxa_poupanca": taxa_poupanca,
            "fixos_pct": fixos_pct,
            "cartoes_pct": cartoes_pct,
            "top": top,
        }

    def generate_text_insights_multi(self, meses, top, detailed=False):
        if not meses:
            self.insights_text.insert("end", "Sem dados para analisar.")
            return
        m = self.calculate_insights_metrics(meses, top)
        lines = [
            f"Período: {self.period_label(meses)}",
            f"Despesas: {brl(m['total_despesas'])}",
            f"Receitas: {brl(m['total_receitas'])}",
            f"Saldo: {brl(m['saldo'])}",
            f"Fixos: {m['fixos_pct']:.1f}% | Cartões: {m['cartoes_pct']:.1f}%"
        ]
        if m["total_receitas"]:
            if m["taxa_poupanca"] >= 20:
                lines.append("Saúde: boa margem de sobra.")
            elif m["taxa_poupanca"] >= 10:
                lines.append("Saúde: atenção moderada.")
            else:
                lines.append("Saúde: alerta de baixa sobra.")
        else:
            lines.append("Cadastre receitas para medir saldo real.")
        if top:
            lines.append(f"Maior gasto: {top[0][0]} ({brl(top[0][1])}).")
        self.insights_text.insert("end", "\n".join(lines))

    def show_detailed_insights(self):
        meses = self.selected_insight_months()
        categoria = self.insight_category_var.get() if hasattr(self, "insight_category_var") else "Todas"
        top = self.top_categories_for_months(meses, categoria)
        m = self.calculate_insights_metrics(meses, top)

        win = tk.Toplevel(self)
        win.title("Análise detalhada")
        win.geometry("760x620")
        win.configure(bg="#f4f6fb")
        box = ttk.Frame(win, style="Card.TFrame", padding=14)
        box.pack(fill="both", expand=True, padx=14, pady=14)
        txt = tk.Text(box, wrap="word", bg="white", relief="flat", font=("Segoe UI", 10))
        txt.pack(fill="both", expand=True)

        lines = [
            f"Análise detalhada — {self.period_label(meses)}",
            "",
            f"Despesas totais: {brl(m.get('total_despesas', 0))}",
            f"Média mensal de despesas: {brl(m.get('media_mensal', 0))}",
            f"Receitas totais: {brl(m.get('total_receitas', 0))}",
            f"Saldo do período: {brl(m.get('saldo', 0))}",
            f"Taxa de poupança estimada: {m.get('taxa_poupanca', 0):.1f}%",
            "",
            "Leitura financeira:",
        ]
        if m.get("total_receitas", 0):
            if m.get("taxa_poupanca", 0) >= 20:
                lines.append("• Boa margem: poupar 20% ou mais costuma indicar boa capacidade para reserva, investimentos e imprevistos.")
            elif m.get("taxa_poupanca", 0) >= 10:
                lines.append("• Atenção: existe sobra, mas ainda abaixo de uma zona confortável para acelerar metas.")
            else:
                lines.append("• Alerta: a sobra está baixa. Priorize redução de gastos variáveis e revisão de despesas fixas.")
        else:
            lines.append("• Sem receitas cadastradas, a análise fica limitada a despesas. Cadastre receitas para medir saldo real.")

        lines.append(f"• Fixos: {m.get('fixos_pct', 0):.1f}% das despesas.")
        if m.get("fixos_pct", 0) > 60:
            lines.append("  Fixos acima de 60% reduzem muito a flexibilidade mensal.")
        elif m.get("fixos_pct", 0) > 50:
            lines.append("  Fixos acima de 50% merecem revisão.")
        else:
            lines.append("  Fixos parecem em uma faixa mais administrável.")

        lines.append(f"• Cartões: {m.get('cartoes_pct', 0):.1f}% das despesas.")
        if m.get("cartoes_pct", 0) > 40:
            lines.append("  Cartões acima de 40% podem indicar consumo variável concentrado e difícil de prever.")
        elif m.get("cartoes_pct", 0) > 25:
            lines.append("  Cartões relevantes: vale acompanhar semanalmente.")
        else:
            lines.append("  Cartões parecem menos concentrados no período.")

        if top:
            lines.append("")
            lines.append("Principais gastos:")
            for cat, val in top:
                pct = (val / m.get("total_despesas", 1) * 100) if m.get("total_despesas") else 0
                lines.append(f"• {cat}: {brl(val)} ({pct:.1f}%)")

        lines.append("")
        lines.append("Próximas ações sugeridas:")
        lines.append("• Revise primeiro categorias de maior peso no gráfico de pizza.")
        lines.append("• Se cartões estiverem altos, acompanhe semanalmente antes do fechamento.")
        lines.append("• Se fixos estiverem altos, avalie renegociação de aluguel, escola, parcelas ou serviços.")
        lines.append("• Use o controle de vencimentos para evitar multas e juros.")

        txt.insert("end", "\n".join(lines))
        txt.configure(state="disabled")

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
