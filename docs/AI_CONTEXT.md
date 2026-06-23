# AI Context — Finanças App

> Documento de contexto para assistentes de IA e novos colaboradores.  
> Versão base oficial: **v3.4.3**

## O que é este projeto

Aplicação desktop de **finanças pessoais** em Python, com interface gráfica Tkinter/ttkbootstrap. O usuário controla despesas mensais por categoria, acompanha vencimentos, receitas, metas e insights visuais. Funciona **offline** com SQLite local e, opcionalmente, sincroniza com **Supabase** quando configurado via `.env`.

## Stack e restrições

| Item | Detalhe |
|------|---------|
| Linguagem | Python 3 |
| UI | `tkinter`, `ttk`, `ttkbootstrap` (opcional) |
| Gráficos | `matplotlib` (opcional, com fallback em canvas) |
| Banco local | SQLite (`financas.db`) |
| Cloud | Supabase (`supabase` Python SDK) |
| Config | `.env` (não versionado) + `config.py` |

**Regra importante:** alterações de código não devem quebrar o modo offline. Supabase é opcional.

## Estrutura de pastas

```text
financas-app/
├── main.py              # Entry point
├── financas_app.py      # Wrapper de compatibilidade
├── config.py            # Constantes, categorias, dados iniciais
├── db.py                # SQLite, sync Supabase, fila assíncrona
├── utils.py             # Formatação BRL, datas, status de pagamento
├── ui/
│   └── app.py           # Interface gráfica
├── sql/
│   └── supabase_schema.sql
├── docs/                # Documentação do projeto
└── requirements.txt
```

## Fluxo de execução

1. `main.py` → `init_db()` → `App().mainloop()`
2. `init_db()` cria/migra tabelas SQLite, seed de categorias e dados iniciais
3. Se `.env` tem `SUPABASE_URL` + `SUPABASE_KEY`, faz `pull_supabase_to_local()` na abertura
4. UI lê sempre do **SQLite local** (`query()` → `_query_local`)
5. Escritas vão para SQLite + fila assíncrona para Supabase (`execute()` → `enqueue_cloud_write`)

## Tabelas principais

| Tabela | Propósito |
|--------|-----------|
| `lancamentos` | Despesa por mês/categoria (UNIQUE mes+categoria) |
| `receitas` | Entradas de caixa |
| `metas` | Metas financeiras com progresso |
| `categorias` | Cadastro de categorias, vencimento, recorrência |
| `pendencias_ignoradas` | Pendências marcadas como regularizadas na UI |

## Abas da interface

1. **Dashboard** — visão do mês: totais, gráficos, gastos em aberto
2. **Lançamentos** — CRUD de despesas, controle de pagamentos, próximos gastos
3. **Insights** — gráficos e diagnóstico por período/categoria
4. **Fluxo de caixa** — receitas e saldo projetado
5. **Metas** — cadastro e acompanhamento de metas

## Botões do cabeçalho

| Botão | Função |
|-------|--------|
| Validar banco de dados | `test_connection()` |
| Sincronizar base | Envia SQLite → Supabase (`sync_local_to_supabase`) |
| Recarregar dados | Sync bidirecional (`sync_two_way`) |
| Restaurar anterior | Restaura `backups/estado_anterior.db` |

## Onde mexer para cada tipo de mudança

| Objetivo | Arquivo(s) |
|----------|------------|
| Nova categoria padrão / regra de negócio | `config.py` |
| Schema, sync, queries | `db.py` |
| Formatação, status, datas | `utils.py` |
| Layout, telas, eventos | `ui/app.py` |
| Schema cloud | `sql/supabase_schema.sql` |
| Versão exibida | `config.py` → `APP_VERSION` |

## Armadilhas conhecidas

- `ui/app.py` concentra toda a interface — refatoração planejada no roadmap.
- Migrações SQLite usam `ALTER TABLE` com try/except (padrão incremental, não Alembic).
- `CATEGORIAS_PADRAO` em `config.py` é mutável em runtime pela UI.
- Não commitar `.env` nem `financas.db`.

## Convenções do projeto

- Valores monetários: função `brl()` e `parse_valor()` em `utils.py`
- Meses no formato `YYYY-MM`
- Status de lançamento: `Pago`, `Não pago`, `Débito automático`
- Backups automáticos antes de operações destrutivas via `backup_database(motivo)`
- Mensagens de UI em português brasileiro

## Comandos úteis

```bash
pip install -r requirements.txt
# Opcional (Supabase):
pip install -r requirements-cloud.txt
python main.py
# ou
python financas_app.py
```

## Documentos relacionados

- [ARCHITECTURE.md](./ARCHITECTURE.md) — arquitetura detalhada
- [SETUP_DESENVOLVIMENTO.md](./SETUP_DESENVOLVIMENTO.md) — ambiente de desenvolvimento
- [DECISIONS.md](./DECISIONS.md) — decisões técnicas registradas
- [ROADMAP.md](./ROADMAP.md) — direção futura
- [CHANGELOG.md](./CHANGELOG.md) — histórico de versões
