"""Camada de banco de dados, backups e categorias."""

import csv
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

from config import DB_FILE, BACKUP_DIR, EXPORT_DIR, CATEGORIAS_PADRAO, CONTAS_RECORRENTES, DADOS_INICIAIS

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
