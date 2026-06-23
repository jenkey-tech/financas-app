# AI Context — App de Finanças Pessoais

Este documento orienta agentes de IA e desenvolvedores sobre o estado atual do repositório **antes de qualquer refatoração**.

## Visão geral

Aplicação desktop de **finanças pessoais** em Python, com interface gráfica Tkinter e persistência em SQLite. O foco é controle mensal de despesas recorrentes (cartões, contas fixas, débitos automáticos), projeção de gastos, insights visuais e fluxo de caixa simplificado.

## Versão canônica do código

| Item | Valor |
|------|-------|
| Versão da aplicação | **v1.6.1** (`APP_VERSION` em `financas_app_v1.6.1/config.py`) |
| Pasta canônica | `financas_app_v1.6.1/` |
| Ponto de entrada | `python main.py` ou `python financas_app.py` (ponte de compatibilidade) |
| Banco de dados | `financas.db` (SQLite, na raiz da pasta da versão) |
| Dependência externa | `matplotlib>=3.8` (opcional; gráficos degradam para canvas Tk se ausente) |

## Estrutura do repositório

```
financas-app/
├── financas_app.py          # Legado monolítico na raiz (v5 simplificada)
├── financas.db              # Banco legado na raiz
├── requirements.txt
├── README.md
├── financas_app_v1.4.0/     # Snapshots históricos versionados
├── financas_app_v1.4.1/
├── financas_app_v1.5.1/
├── financas_app_v1.5.2/
├── financas_app_v1.6.1/     # ← Versão atual e mais completa
└── docs/                    # Documentação oficial (este diretório)
```

**Importante:** pastas `financas_app_v1.x.x/` são **artefatos históricos** preservados no Git. A base funcional a documentar e evoluir é `financas_app_v1.6.1/`.

## Stack tecnológica

- **Linguagem:** Python 3 (stdlib + Tkinter)
- **UI:** `tkinter` + `ttk` (tema `clam`, estilo customizado)
- **Gráficos:** Matplotlib com backend `TkAgg`
- **Banco:** SQLite via `sqlite3` (sem ORM)
- **Integração Git:** `subprocess` para commit local a partir da UI

## Módulos principais (v1.6.1)

| Arquivo | Responsabilidade |
|---------|------------------|
| `main.py` | Bootstrap: `init_db()` + loop da UI |
| `config.py` | Constantes, categorias padrão, contas recorrentes, dados iniciais |
| `db.py` | Schema SQLite, queries, backups, export CSV, CRUD de categorias |
| `utils.py` | Formatação BRL, parse de valores, datas de vencimento, status de pagamento |
| `ui/app.py` | Classe `App(tk.Tk)` — toda a interface e orquestração (~1460 linhas) |
| `services/*.py` | Re-exports finos; lógica ainda concentrada em `ui/app.py` e `db.py` |

## Modelo de dados (SQLite)

- **`lancamentos`** — despesas mensais por categoria (`UNIQUE(mes, categoria)`)
- **`receitas`** — entradas de renda por mês
- **`metas`** — metas financeiras com valor alvo e atual
- **`categorias`** — catálogo configurável (vencimento, tipo manual/débito, recorrente, ativa)
- **`pendencias_ignoradas`** — pendências regularizadas/ignoradas na lista de próximos gastos

## Regras de negócio críticas

1. **Categorias acumulativas** (`CATEGORIAS_ACUMULATIVAS`): lançamento duplicado no mesmo mês **soma** automaticamente (ex.: cartões, Ifood).
2. **Categorias fixas** (`CATEGORIAS_FIXAS`): duplicata pergunta somar / substituir / cancelar.
3. **Status de pagamento:** calculado por vencimento, tipo (manual vs débito automático) e `status_lancamento` (Pago, Não pago, Débito automático).
4. **Sugestão de valor:** últimos 6 lançamentos da categoria; detecta valor recorrente se 3 meses consecutivos iguais.
5. **Projeção mensal:** pago + não pago + pendente estimado (categorias recorrentes sem lançamento usam sugestão histórica).
6. **Backups automáticos:** operações sensíveis chamam `backup_database(motivo)` antes de alterar dados.

## Abas da interface

1. **Lançamentos** — cards resumo, filtro de mês, formulário, controle de pagamentos, próximos gastos
2. **Insights e gráficos** — evolução, pizza top gastos, saúde financeira, resumo textual
3. **Fluxo de caixa** — receitas vs despesas, saldo projetado
4. **Metas** — cadastro e acompanhamento de metas financeiras

## Convenções de código

- Formato monetário brasileiro via `brl()` e `parse_valor()` (aceita `1.234,56` e `1234.56`)
- CSV com delimitador `;` e encoding `utf-8-sig`
- Meses no formato `YYYY-MM`
- Commits de dados via botão UI: mensagem `dados YYYY-MM-DD HH:MM`
- Backup de estado anterior: `backups/estado_anterior.db` (único ponto de restauração)

## O que NÃO fazer sem alinhamento

- Não mover ou apagar pastas históricas `financas_app_v1.x.x/` sem plano de migração
- Não alterar schema SQLite sem migração explícita (dados reais em produção)
- Não assumir que `financas_app.py` na raiz é a versão atual — usar `financas_app_v1.6.1/`
- Não adicionar dependências pesadas; app deve rodar com Python + Tkinter nativos

## Referências internas

- Arquitetura detalhada: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Setup local: [SETUP_DESENVOLVIMENTO.md](./SETUP_DESENVOLVIMENTO.md)
- Decisões técnicas: [DECISIONS.md](./DECISIONS.md)
- Histórico de versões: [CHANGELOG.md](./CHANGELOG.md)
- Próximos passos: [ROADMAP.md](./ROADMAP.md)
