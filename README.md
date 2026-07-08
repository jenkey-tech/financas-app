# Finanças App

Aplicação desktop de **finanças pessoais** em Python, com interface gráfica moderna (Tkinter + ttkbootstrap), controle de despesas por categoria, dashboard, insights visuais, fluxo de caixa e metas.

Funciona **100% offline** com SQLite. A sincronização com **Supabase** é opcional, para quem quiser replicar dados entre dispositivos.

**Versão:** 3.4.3 · **Licença:** MIT

---

## Destaques

- Dashboard com gráficos de composição e status de pagamentos
- Controle de vencimentos, débito automático e próximos gastos
- Insights com tendências, top categorias e recomendações
- Fluxo de caixa e metas financeiras
- Sync cloud opcional (SQLite local + fila assíncrona para Supabase)
- Dados de demonstração fictícios disponíveis apenas via `seed_demo_data()` (chamada manual)

---

## Stack

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.10+ |
| Interface | Tkinter, ttk, ttkbootstrap |
| Gráficos | matplotlib |
| Banco local | SQLite |
| Cloud (opcional) | Supabase |

---

## Como executar

### 1. Clonar e instalar

```powershell
git clone https://github.com/jenkey-tech/financas-app.git
cd financas-app
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Rodar (modo offline)

```powershell
python main.py
```

Na primeira execução, o app cria `financas.db` localmente **sem inserir dados de demonstração automaticamente**.

Para popular dados fictícios de demo/teste, chame explicitamente `seed_demo_data()` em `db.py` (por exemplo via shell Python). Esses dados ficam marcados com `is_demo=1` e **não são enviados** ao Supabase pela sincronização.

### 3. Sync com Supabase (opcional)

```powershell
pip install -r requirements-cloud.txt
copy .env.example .env
```

Preencha `.env` com um projeto **seu** (recomendado: projeto separado só para testes):

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_public
```

Execute `sql/supabase_schema.sql` no SQL Editor do Supabase, abra o app e use **Validar banco de dados** → **Recarregar dados**.

> **Segurança:** nunca commite `.env`, `*.db`, backups ou exports. Para uso real em produção, habilite RLS e autenticação no Supabase.

---

## Estrutura do projeto

```text
financas-app/
├── main.py                 # Ponto de entrada
├── financas_app.py         # Compatibilidade com execução antiga
├── config.py               # Constantes e seed de demonstração
├── db.py                   # SQLite, sync Supabase, fila cloud
├── utils.py                # Formatação BRL, datas, status
├── ui/
│   └── app.py              # Interface gráfica
├── sql/
│   └── supabase_schema.sql # Schema cloud opcional
├── docs/                   # Documentação técnica
├── requirements.txt
└── requirements-cloud.txt  # Supabase (opcional)
```

---

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura e fluxo de dados |
| [docs/SETUP_DESENVOLVIMENTO.md](docs/SETUP_DESENVOLVIMENTO.md) | Ambiente de desenvolvimento |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Decisões técnicas (ADR) |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Evolução planejada |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |
| [docs/REPOSITORIOS.md](docs/REPOSITORIOS.md) | Repositório público vs. desenvolvimento privado |

---

## O que não vai para o Git

- `.env` — credenciais Supabase
- `financas.db` — banco local com seus lançamentos
- `backups/`, `exports/` — snapshots pessoais
- `*.csv`, `*.xlsx` — planilhas com dados reais

---

## Desenvolvimento

Este repositório é a **versão pública de portfólio**, sem histórico sensível e sem automações Git embutidas na interface.

O desenvolvimento diário pode ser feito em um repositório privado separado; alterações estáveis são publicadas aqui via cherry-pick ou cópia manual de módulos.

---

## Licença

MIT — veja [LICENSE](LICENSE).
