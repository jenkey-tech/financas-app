"""Camada de banco de dados local SQLite e sincronização Supabase.

v2.0.0 mantém o app funcionando offline com SQLite local e adiciona
sincronização opcional com Supabase quando SUPABASE_URL e SUPABASE_KEY
estão configurados no arquivo .env.
"""

import csv
import os
import sqlite3
import shutil
import threading
import queue
import atexit
from pathlib import Path
from datetime import datetime

from config import DB_FILE, BACKUP_DIR, EXPORT_DIR, CATEGORIAS_PADRAO, CONTAS_RECORRENTES, DADOS_INICIAIS


def load_dotenv(path=".env"):
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()

_STARTUP_PULL_DONE = False
_SYNCING_FROM_CLOUD = False

# Fila de gravação cloud para não travar a interface.
# O app grava primeiro no SQLite local e envia para o Supabase em segundo plano.
_CLOUD_WRITE_QUEUE = queue.Queue()
_CLOUD_WORKER_STARTED = False
_CLOUD_WORKER_LOCK = threading.Lock()
_CLOUD_WRITE_ERRORS = []


def _cloud_worker():
    while True:
        item = _CLOUD_WRITE_QUEUE.get()
        try:
            if item is None:
                return
            sql, params = item
            try:
                _execute_supabase(sql, params)
            except Exception as exc:
                _CLOUD_WRITE_ERRORS.append(str(exc))
        finally:
            _CLOUD_WRITE_QUEUE.task_done()


def _ensure_cloud_worker():
    global _CLOUD_WORKER_STARTED
    if _CLOUD_WORKER_STARTED:
        return
    with _CLOUD_WORKER_LOCK:
        if _CLOUD_WORKER_STARTED:
            return
        worker = threading.Thread(target=_cloud_worker, daemon=True)
        worker.start()
        _CLOUD_WORKER_STARTED = True


def enqueue_cloud_write(sql, params=()):
    if not using_supabase():
        return
    _ensure_cloud_worker()
    _CLOUD_WRITE_QUEUE.put((sql, tuple(params)))


def flush_cloud_writes(timeout=None):
    """Espera envios pendentes terminarem. Usado antes de sincronização manual."""
    if not using_supabase():
        return
    _CLOUD_WRITE_QUEUE.join()


def last_cloud_errors():
    return list(_CLOUD_WRITE_ERRORS[-5:])




def using_supabase():
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"))


def connection_mode():
    return "Supabase Cloud + cache rápido" if using_supabase() else "SQLite local"


def get_supabase_client():
    if not using_supabase():
        raise RuntimeError("Supabase não está configurado. Preencha SUPABASE_URL e SUPABASE_KEY no arquivo .env.")
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("Pacote supabase não instalado. Rode: pip install -r requirements.txt") from exc
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


def db_path():
    return Path(DB_FILE)


def get_connection():
    return sqlite3.connect(DB_FILE)


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
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mes, categoria)
        )
    """)
    for stmt in [
        "ALTER TABLE lancamentos ADD COLUMN status_lancamento TEXT DEFAULT 'Pago'",
        "ALTER TABLE lancamentos ADD COLUMN updated_at TEXT",
    ]:
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS receitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            observacao TEXT DEFAULT '',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE receitas ADD COLUMN updated_at TEXT")
    except sqlite3.OperationalError:
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            valor_alvo REAL NOT NULL,
            valor_atual REAL DEFAULT 0,
            observacao TEXT DEFAULT '',
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE metas ADD COLUMN updated_at TEXT")
    except sqlite3.OperationalError:
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            dia_vencimento INTEGER,
            tipo TEXT DEFAULT 'manual',
            recorrente INTEGER DEFAULT 0,
            ativa INTEGER DEFAULT 1,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try:
        cur.execute("ALTER TABLE categorias ADD COLUMN updated_at TEXT")
    except sqlite3.OperationalError:
        pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pendencias_ignoradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            categoria TEXT NOT NULL,
            vencimento TEXT NOT NULL,
            motivo TEXT DEFAULT 'regularizado',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mes, categoria, vencimento)
        )
    """)
    try:
        cur.execute("ALTER TABLE pendencias_ignoradas ADD COLUMN updated_at TEXT")
    except sqlite3.OperationalError:
        pass

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

    # Migrações de nomes legados (apenas registros com categorias antigas de versões anteriores).
    cur.execute("UPDATE lancamentos SET categoria='Cartão Alpha' WHERE categoria='Cartão Legado 1'")
    cur.execute("UPDATE lancamentos SET categoria='Cartão Beta dia 15' WHERE categoria='Cartão Legado 2'")
    cur.execute("UPDATE lancamentos SET categoria='Condomínio' WHERE categoria='Condomínio Legado'")
    cur.execute("SELECT COUNT(*) FROM lancamentos")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT OR REPLACE INTO lancamentos (mes, categoria, valor, status_lancamento) VALUES (?, ?, ?, 'Pago')",
            DADOS_INICIAIS
        )
    for table in ["lancamentos", "receitas", "metas", "categorias", "pendencias_ignoradas"]:
        try:
            cur.execute(f"UPDATE {table} SET updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)")
        except sqlite3.OperationalError:
            pass
    con.commit()
    con.close()

    # v3.0.2: Supabase é a fonte oficial, mas a tela usa cache local rápido.
    # Ao abrir o app, puxa os dados da nuvem uma única vez para evitar versões novas desatualizadas.
    global _STARTUP_PULL_DONE
    if using_supabase() and not _STARTUP_PULL_DONE:
        _STARTUP_PULL_DONE = True
        try:
            pull_supabase_to_local()
        except Exception:
            # Não impede abertura do app; usuário pode usar "Recarregar dados".
            pass



def table_columns_sqlite(table):
    con = sqlite3.connect(DB_FILE)
    try:
        return [row[1] for row in con.execute(f"PRAGMA table_info({table})").fetchall()]
    finally:
        con.close()


def ensure_local_schema_for_sync():
    """Garante colunas usadas na sincronização mesmo em bancos antigos."""
    init_db()
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    migrations = {
        "lancamentos": [
            ("status_lancamento", "TEXT DEFAULT 'Pago'"),
            ("updated_at", "TEXT"),
        ],
        "receitas": [("updated_at", "TEXT")],
        "metas": [("updated_at", "TEXT")],
        "categorias": [("updated_at", "TEXT")],
        "pendencias_ignoradas": [("updated_at", "TEXT")],
    }
    for table, columns in migrations.items():
        existing = [row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        for name, ddl in columns:
            if name not in existing:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}")
        # SQLite não permite DEFAULT CURRENT_TIMESTAMP ao adicionar coluna.
        # Por isso a coluna é criada simples e preenchida em seguida.
        refreshed = [row[1] for row in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        if "updated_at" in refreshed:
            cur.execute(f"UPDATE {table} SET updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)")
    con.commit()
    con.close()


def _is_select(sql):
    return sql.strip().lower().startswith("select")


def _table_from_simple_select(sql):
    lower = sql.lower()
    if " from " not in lower:
        return None
    after = lower.split(" from ", 1)[1].strip()
    table = after.split()[0].strip().strip(";")
    return table



SUPABASE_TABLES = {
    "lancamentos": ["id", "mes", "categoria", "valor", "observacao", "status_lancamento", "updated_at"],
    "receitas": ["id", "mes", "descricao", "valor", "observacao", "updated_at"],
    "metas": ["id", "nome", "valor_alvo", "valor_atual", "observacao", "updated_at"],
    "categorias": ["id", "nome", "dia_vencimento", "tipo", "recorrente", "ativa", "updated_at"],
    "pendencias_ignoradas": ["id", "mes", "categoria", "vencimento", "motivo", "criado_em", "updated_at"],
}

# Alias defensivo para compatibilidade com chamadas antigas.
supabase_tables = SUPABASE_TABLES

def _supabase_select(sql, params=()):
    """Atende às consultas SELECT usadas pelo app via Supabase.

    Para consultas mais complexas ou não mapeadas, usa SQLite local como fallback.
    """
    client = get_supabase_client()
    lower = " ".join(sql.lower().split())

    # COUNT e SUM específicos
    if "count(*) from lancamentos" in lower:
        result = client.table("lancamentos").select("id", count="exact").limit(1).execute()
        return [(result.count or 0,)]

    if "coalesce(sum(valor),0) from lancamentos" in lower:
        table = "lancamentos"
    elif "coalesce(sum(valor),0) from receitas" in lower:
        table = "receitas"
    else:
        table = None

    if table:
        rows = client.table(table).select("valor").execute().data or []
        if "where mes=?" in lower and params:
            rows = [r for r in rows if r.get("mes") == params[0]]
        elif "where mes in" in lower and params:
            allowed = set(params)
            rows = [r for r in rows if r.get("mes") in allowed]
        return [(sum(float(r.get("valor") or 0) for r in rows),)]

    # Distinct meses/categorias
    if "select distinct mes from lancamentos" in lower:
        rows = client.table("lancamentos").select("mes").execute().data or []
        meses = sorted({r.get("mes") for r in rows if r.get("mes")}, reverse="desc" in lower)
        return [(m,) for m in meses]

    if "select distinct categoria from lancamentos" in lower:
        rows = client.table("lancamentos").select("categoria").execute().data or []
        cats = sorted({r.get("categoria") for r in rows if r.get("categoria")})
        return [(c,) for c in cats]

    # Monthly totals
    if "select mes, sum(valor) from lancamentos group by mes order by mes" in lower:
        rows = client.table("lancamentos").select("mes,valor").execute().data or []
        totals = {}
        for r in rows:
            mes = r.get("mes")
            if mes:
                totals[mes] = totals.get(mes, 0) + float(r.get("valor") or 0)
        return [(m, totals[m]) for m in sorted(totals)]

    # GROUP BY categoria com SUM
    if "select categoria, sum(valor)" in lower and "from lancamentos" in lower:
        rows = client.table("lancamentos").select("mes,categoria,valor").execute().data or []
        if "where mes in" in lower and params:
            allowed = set(params)
            rows = [r for r in rows if r.get("mes") in allowed and float(r.get("valor") or 0) > 0]
        elif "where mes=?" in lower and params:
            rows = [r for r in rows if r.get("mes") == params[0] and float(r.get("valor") or 0) > 0]
        totals = {}
        for r in rows:
            cat = r.get("categoria")
            if cat:
                totals[cat] = totals.get(cat, 0) + float(r.get("valor") or 0)
        result = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        if "limit" in lower:
            try:
                lim = int(lower.rsplit("limit", 1)[1].strip().split()[0])
                result = result[:lim]
            except Exception:
                pass
        return result

    # SELECT simples por tabela
    table = _table_from_simple_select(sql)
    if table in SUPABASE_TABLES:
        # Colunas pedidas
        select_part = sql.lower().split(" from ", 1)[0].replace("select", "", 1).strip()
        original_select = sql.split(" FROM ", 1)[0] if " FROM " in sql else sql.split(" from ", 1)[0]
        original_cols = original_select.replace("SELECT", "").replace("select", "").strip()
        cols = [c.strip() for c in original_cols.split(",")]
        if cols == ["*"]:
            cols = SUPABASE_TABLES[table]

        rows = client.table(table).select(",".join(cols)).execute().data or []

        # Filtros usados pelo app
        if "where mes=?" in lower and params:
            rows = [r for r in rows if r.get("mes") == params[0]]
        if "where categoria=?" in lower and params:
            rows = [r for r in rows if r.get("categoria") == params[0]]
        if "where mes=? and categoria=?" in lower and len(params) >= 2:
            rows = [r for r in rows if r.get("mes") == params[0] and r.get("categoria") == params[1]]
        if "where ativa=1" in lower:
            rows = [r for r in rows if int(r.get("ativa") or 0) == 1]
        if "where recorrente=1 and ativa=1" in lower:
            rows = [r for r in rows if int(r.get("recorrente") or 0) == 1 and int(r.get("ativa") or 0) == 1]
        if "where mes in" in lower and params:
            allowed = set(params)
            rows = [r for r in rows if r.get("mes") in allowed]
        if "and valor > 0" in lower or "where valor > 0" in lower:
            rows = [r for r in rows if float(r.get("valor") or 0) > 0]

        # Ordenações principais
        if "order by valor desc" in lower:
            rows = sorted(rows, key=lambda r: float(r.get("valor") or 0), reverse=True)
        elif "order by mes desc" in lower:
            rows = sorted(rows, key=lambda r: r.get("mes") or "", reverse=True)
        elif "order by mes" in lower:
            rows = sorted(rows, key=lambda r: r.get("mes") or "")
        elif "order by nome" in lower:
            rows = sorted(rows, key=lambda r: r.get("nome") or "")
        elif "order by categoria" in lower:
            rows = sorted(rows, key=lambda r: r.get("categoria") or "")
        elif "order by id desc" in lower:
            rows = sorted(rows, key=lambda r: int(r.get("id") or 0), reverse=True)

        if "limit" in lower:
            try:
                lim = int(lower.rsplit("limit", 1)[1].strip().split()[0])
                rows = rows[:lim]
            except Exception:
                pass

        return [tuple(r.get(c) for c in cols) for r in rows]

    # Fallback local para consultas não mapeadas
    return _query_local(sql, params)


def _query_local(sql, params=()):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()
    return rows


def query(sql, params=()):
    # Leitura local-first para manter a interface rápida.
    # Use "Atualizar nuvem" para puxar dados de outro computador.
    return _query_local(sql, params)


def _execute_local(sql, params=()):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(sql, params)
    con.commit()
    con.close()


def _execute_supabase(sql, params=()):
    client = get_supabase_client()
    lower = " ".join(sql.lower().split())

    if lower.startswith("insert into lancamentos"):
        # save_entry usa INSERT com mes,categoria,valor,observacao,status
        item = {
            "mes": params[0],
            "categoria": params[1],
            "valor": params[2],
            "observacao": params[3] if len(params) > 3 else "",
            "status_lancamento": params[4] if len(params) > 4 else "Pago",
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        client.table("lancamentos").upsert(item, on_conflict="mes,categoria").execute()
        return

    if lower.startswith("update lancamentos set valor=?, observacao=?, status_lancamento=?"):
        item = {
            "mes": params[3],
            "categoria": params[4],
            "valor": params[0],
            "observacao": params[1],
            "status_lancamento": params[2],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        client.table("lancamentos").upsert(item, on_conflict="mes,categoria").execute()
        return

    if lower.startswith("update lancamentos set valor=?"):
        client.table("lancamentos").update({
            "valor": params[0],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }).eq("mes", params[1]).eq("categoria", params[2]).execute()
        return

    if lower.startswith("update lancamentos set status_lancamento=?"):
        client.table("lancamentos").update({
            "status_lancamento": params[0],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }).eq("mes", params[1]).eq("categoria", params[2]).execute()
        return

    if lower.startswith("update lancamentos set categoria=?"):
        client.table("lancamentos").update({
            "categoria": params[0],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }).eq("mes", params[1]).eq("categoria", params[2]).execute()
        return

    if lower.startswith("delete from lancamentos"):
        client.table("lancamentos").delete().eq("mes", params[0]).eq("categoria", params[1]).execute()
        return

    if lower.startswith("insert into receitas"):
        item = {
            "mes": params[0],
            "descricao": params[1],
            "valor": params[2],
            "observacao": params[3] if len(params) > 3 else "",
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        client.table("receitas").insert(item).execute()
        return

    if lower.startswith("delete from receitas"):
        client.table("receitas").delete().eq("id", params[0]).execute()
        return

    if lower.startswith("insert into metas"):
        item = {
            "nome": params[0],
            "valor_alvo": params[1],
            "valor_atual": params[2],
            "observacao": params[3],
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        client.table("metas").insert(item).execute()
        return

    if lower.startswith("delete from metas"):
        client.table("metas").delete().eq("id", params[0]).execute()
        return

    if lower.startswith("update categorias set ativa=0"):
        client.table("categorias").update({"ativa": 0, "updated_at": datetime.now().isoformat(timespec="seconds")}).eq("nome", params[0]).execute()
        return

    if lower.startswith("insert into categorias") or lower.startswith("update categorias"):
        # upsert_category deve cuidar do caso principal
        return

    if lower.startswith("insert into pendencias_ignoradas") or lower.startswith("insert or replace into pendencias_ignoradas"):
        item = {
            "mes": params[0],
            "categoria": params[1],
            "vencimento": params[2],
            "motivo": params[3] if len(params) > 3 else "regularizado",
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        client.table("pendencias_ignoradas").upsert(item, on_conflict="mes,categoria,vencimento").execute()
        return

    # Fallback: executa local se o comando não foi mapeado.
    _execute_local(sql, params)


def execute(sql, params=()):
    # Resposta rápida: grava localmente e envia para a nuvem em segundo plano.
    local_error = None
    try:
        _execute_local(sql, params)
    except Exception as exc:
        local_error = exc
    if using_supabase():
        enqueue_cloud_write(sql, params)
    if local_error and not using_supabase():
        raise local_error


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
    item = {
        "nome": nome,
        "dia_vencimento": dia_vencimento,
        "tipo": tipo,
        "recorrente": int(recorrente),
        "ativa": int(ativa),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    # Local cache
    _execute_local("""
        INSERT INTO categorias (nome, dia_vencimento, tipo, recorrente, ativa, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(nome) DO UPDATE SET
            dia_vencimento=excluded.dia_vencimento,
            tipo=excluded.tipo,
            recorrente=excluded.recorrente,
            ativa=excluded.ativa,
            updated_at=excluded.updated_at
    """, (nome, dia_vencimento, tipo, int(recorrente), int(ativa), item["updated_at"]))

    if using_supabase():
        client = get_supabase_client()
        client.table("categorias").upsert(item, on_conflict="nome").execute()


def test_connection():
    if using_supabase():
        client = get_supabase_client()
        result = client.table("lancamentos").select("id", count="exact").limit(1).execute()
        return result.count or 0
    init_db()
    return query("SELECT COUNT(*) FROM lancamentos")[0][0]



def _rows_as_dicts(table):
    ensure_local_schema_for_sync()
    cols = supabase_tables[table] if "supabase_tables" in globals() else SUPABASE_TABLES[table]
    available = table_columns_sqlite(table)
    select_cols = [c for c in cols if c in available]
    rows = query(f"SELECT {','.join(select_cols)} FROM {table}")
    result = []
    for row in rows:
        item = dict(zip(select_cols, row))
        if "updated_at" in cols and not item.get("updated_at"):
            item["updated_at"] = datetime.now().isoformat(timespec="seconds")
        if table == "lancamentos" and not item.get("status_lancamento"):
            item["status_lancamento"] = "Pago"
        result.append(item)
    return result


def sync_local_to_supabase():
    if not using_supabase():
        raise RuntimeError("Supabase não configurado. Preencha SUPABASE_URL e SUPABASE_KEY no .env.")
    ensure_local_schema_for_sync()
    client = get_supabase_client()
    total = 0
    for table in supabase_tables:
        rows = _rows_as_dicts(table)
        if not rows:
            continue
        if table == "lancamentos":
            client.table(table).upsert(rows, on_conflict="mes,categoria").execute()
        elif table == "categorias":
            client.table(table).upsert(rows, on_conflict="nome").execute()
        elif table == "pendencias_ignoradas":
            client.table(table).upsert(rows, on_conflict="mes,categoria,vencimento").execute()
        else:
            client.table(table).upsert(rows).execute()
        total += len(rows)
    return total


def pull_supabase_to_local():
    """Baixa dados do Supabase para o SQLite local sem reenviar para a nuvem."""
    if not using_supabase():
        return 0
    client = get_supabase_client()
    total = 0
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    try:
        for table, cols in supabase_tables.items():
            result = client.table(table).select("*").execute()
            rows = result.data or []
            if not rows:
                continue

            # Remove ids nulos e colunas inexistentes no local de forma defensiva.
            local_cols = table_columns_sqlite(table)
            insert_cols = [c for c in cols if c in local_cols and any(c in row for row in rows)]
            placeholders = ",".join("?" for _ in insert_cols)
            col_list = ",".join(insert_cols)
            sql = f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})"
            for item in rows:
                cur.execute(sql, tuple(item.get(c) for c in insert_cols))
                total += 1
        con.commit()
        return total
    finally:
        con.close()


def sync_supabase_to_local():
    if not using_supabase():
        raise RuntimeError("Supabase não configurado. Preencha SUPABASE_URL e SUPABASE_KEY no .env.")
    ensure_local_schema_for_sync()
    return pull_supabase_to_local()


def sync_two_way():
    # Envia pendências locais e depois puxa o estado da nuvem.
    enviados = sync_local_to_supabase()
    recebidos = sync_supabase_to_local()
    return enviados, recebidos
