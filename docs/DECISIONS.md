# Decisões técnicas — Finanças App

Registro de decisões arquiteturais relevantes (ADR simplificado).  
Base: **v3.4.3**

---

## ADR-001 — Desktop com Tkinter

**Data:** v1.0.0 (evolução contínua)  
**Status:** Aceita

### Contexto

Finanças pessoais com uso individual, sem necessidade inicial de acesso remoto via browser.

### Decisão

Usar Python + Tkinter como stack de UI desktop nativa.

### Consequências

- (+) Simples de rodar localmente, sem servidor
- (+) Funciona offline por padrão
- (−) UI monolítica em `ui/app.py`
- (−) Distribuição depende de Python instalado ou empacotamento futuro

---

## ADR-002 — SQLite como cache local obrigatório

**Data:** v2.0.0  
**Status:** Aceita

### Contexto

Integração cloud introduziu latência e risco de travamento da UI.

### Decisão

Manter SQLite (`financas.db`) como **fonte de leitura** da interface. Todas as consultas passam por `_query_local()`.

### Consequências

- (+) Interface responsiva
- (+) App funciona sem internet
- (−) Dados podem ficar stale até "Recarregar dados"
- (−) Dois stores para manter consistentes

---

## ADR-003 — Supabase substitui Turso

**Data:** v2.0.0  
**Status:** Aceita (Turso removido)

### Contexto

v1.7.0 usava Turso/libsql. Necessidade de schema SQL visível, sync simples e ecossistema Postgres.

### Decisão

Migrar para Supabase com schema explícito em `sql/supabase_schema.sql`. Remover dependência `libsql`.

### Consequências

- (+) SQL Editor e dashboard Supabase
- (+) Upsert por chaves naturais (mes+categoria, nome, etc.)
- (−) RLS desabilitado para uso pessoal simplificado
- (−) Credenciais em `.env` (anon key exposta localmente — aceitável para uso single-user)

---

## ADR-004 — Escrita local-first com fila assíncrona para cloud

**Data:** v2.1.1 / v3.0.2  
**Status:** Aceita

### Contexto

Escritas síncronas no Supabase travavam edição de células na tabela de pagamentos.

### Decisão

1. `execute()` grava imediatamente no SQLite
2. Se Supabase configurado, enfileira operação em thread daemon
3. Na abertura, `pull_supabase_to_local()` uma vez
4. Sync manual via botões do cabeçalho

### Consequências

- (+) UX fluida
- (+) Flush ao fechar app (`on_close` → `flush_cloud_writes`)
- (−) Possível perda de envios se app for killado abruptamente
- (−) Erros cloud acumulados em `_CLOUD_WRITE_ERRORS` (últimos 5)

---

## ADR-005 — Refatoração modular v1.5.0

**Data:** v1.5.0  
**Status:** Parcialmente aplicada

### Contexto

Monolito original difícil de manter.

### Decisão

Separar em `config.py`, `db.py`, `utils.py`, `ui/app.py`, `services/`. Manter `financas_app.py` como compat.

### Consequências

- (+) Responsabilidades mais claras na camada de dados
- (−) UI ainda concentra lógica de negócio e imports diretos de `db`
- (−) `services/` permanece fino — evolução pendente

---

## ADR-006 — Categorias acumulativas vs substituíveis

**Data:** v1.x (regras em `config.py`)  
**Status:** Aceita

### Contexto

Cartões e consumo variável (Ifood) recebem lançamentos parciais ao longo do mês; fixos (aluguel) devem substituir.

### Decisão

`CATEGORIAS_ACUMULATIVAS` somam valor ao salvar duplicata no mesmo mês; demais categorias perguntam ao usuário (somar/substituir/cancelar).

### Consequências

- (+) Modela uso real de cartão de crédito
- (−) Lista hardcoded em `config.py` — novas categorias acumulativas exigem código ou gerenciador

---

## ADR-007 — Chave única mes+categoria em lançamentos

**Data:** v1.0.0  
**Status:** Aceita

### Contexto

Uma despesa por categoria por mês é suficiente para o modelo de controle doméstico.

### Decisão

`UNIQUE(mes, categoria)` no SQLite e índice equivalente no Supabase. Upsert usa essa chave.

### Consequências

- (+) Modelo simples, fácil de visualizar
- (−) Múltiplos lançamentos na mesma categoria no mesmo mês exigem soma manual ou observação concatenada

---

## ADR-008 — ttkbootstrap e matplotlib opcionais

**Data:** v3.1.0  
**Status:** Aceita

### Decisão

Importar `ttkbootstrap` e `matplotlib` com try/except; degradar gráficos e tema se ausentes.

### Consequências

- (+) App abre mesmo com dependências parciais
- (−) Experiência visual inconsistente sem pacotes completos

---

## ADR-009 — Git integrado via subprocess (não libgit)

**Data:** v1.5.1  
**Status:** Depreciada (removida na versão pública de portfólio)

### Decisão original

Botão "Commit estado atual" chamava `git add .` e `git commit` via subprocess.

### Motivo da remoção

Risco de versionar acidentalmente `.env`, banco local ou exports em repositório público.
---

## ADR-010 — Repositório público de portfólio

**Data:** 2026-06  
**Status:** Aceita

### Contexto

O histórico Git anterior continha dados financeiros reais em `config.py`. O desenvolvimento diário usa dados pessoais e credenciais locais.

### Decisão

Separar em dois repositórios:

- **Público** (`financas-app`) — portfólio, histórico limpo, dados fictícios, sem automação Git na UI
- **Privado** — desenvolvimento real, `.env`, `financas.db`, backups

### Consequências

- (+) Portfólio seguro para divulgação
- (+) Desenvolvimento privado preservado
- (−) Sincronização manual entre repos (cherry-pick ou cópia de módulos)

---

## ADR-011 — Reinício do código na v3.4.3

**Data:** 2026-06  
**Status:** Aceita

### Contexto

Histórico Git anterior continha branches experimentais e documentação desalinhada.

### Decisão

Base oficial na v3.4.3 com documentação em `docs/` e sanitização de dados de demonstração.

### Consequências

- (+) Base limpa para evolução
- (+) Documentação alinhada ao código
- (−) Histórico anterior não preservado no repo público

---

## Template para novas decisões

```markdown
## ADR-XXX — Título

**Data:** YYYY-MM-DD  
**Status:** Proposta | Aceita | Substituída | Depreciada

### Contexto
...

### Decisão
...

### Consequências
...
```
