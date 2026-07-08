# Incidente: mistura de dados reais e fictícios (PAUSA V4)

## Escopo da investigação

Investigação **somente leitura** no código-fonte, sem sincronização e sem alterações em SQLite/Supabase.

Objetivo: identificar origem de categorias fictícias e risco de terem sido enviadas para a nuvem.

---

## 1) De onde vêm as categorias fictícias citadas

Categorias investigadas:

- Cartão Alpha
- Cartão Beta dia 08
- Cartão Beta dia 15
- Cartão Loja Online
- Escola
- Creche
- IPTU

### Evidência encontrada

Todas aparecem explicitamente em `config.py`:

- `CATEGORIAS_PADRAO` (lista base de categorias)
- `CONTAS_RECORRENTES` (regras recorrentes por dia/tipo)
- `CARTOES` e `FIXOS`
- `DADOS_INICIAIS` (seed de lançamentos fictícios por mês)

Referências diretas:

- `config.py` linhas 12–16 (`CATEGORIAS_PADRAO`)
- `config.py` linhas 18–35 (`CONTAS_RECORRENTES`)
- `config.py` linhas 45–46 (`CARTOES`, `FIXOS`)
- `config.py` linhas 49–70 (`DADOS_INICIAIS`)

---

## 2) Verificação por origem solicitada

## `config.py`

**SIM, contém** as categorias fictícias e os dados de demonstração.

## `DADOS_INICIAIS`

**SIM, contém** lançamentos fictícios para parte dessas categorias (ex.: Cartão Alpha, Cartão Beta dia 15, Escola).

## `CONTAS_RECORRENTES`

**SIM, contém** as categorias citadas como contas recorrentes.

## Banco SQLite local

O arquivo SQLite não estava previamente disponível no workspace durante a investigação, então não houve leitura de dados reais existentes nesta execução.

Pelo fluxo de código, quando o app roda `init_db()`, as categorias acima são inseridas no SQLite local via `INSERT OR IGNORE` em `categorias`.

## Supabase

Não há seed SQL de categorias fictícias em `sql/supabase_schema.sql` (apenas DDL/schema).

Logo, no Supabase esses dados entram por sincronização/app (quando configurado), não pelo script de schema.

---

## 3) `init_db()` faz seed automático dessas categorias?

**SIM.**

Em `db.py`, `init_db()`:

1. insere categorias de `CONTAS_RECORRENTES` em `categorias` (`INSERT OR IGNORE`);
2. insere categorias de `CATEGORIAS_PADRAO` em `categorias` (`INSERT OR IGNORE`);
3. se `lancamentos` estiver vazio (`COUNT(*) == 0`), insere `DADOS_INICIAIS`.

Referências:

- `db.py` linhas 229–238 (seed de categorias)
- `db.py` linhas 245–249 (seed de `DADOS_INICIAIS` quando vazio)

Conclusão: em instalação nova/local vazio, o seed fictício é automático.

---

## 4) A tela lê do SQLite local, Supabase ou ambos?

**Leitura da UI é local (SQLite), com sincronização cloud complementar.**

Evidências:

- UI usa `query(...)` de `db.py` em toda a renderização (`ui/app.py`, vários pontos).
- `query()` retorna `_query_local(...)` diretamente (`db.py` linhas 471–474).
- Ao abrir app, se Supabase estiver configurado, `init_db()` chama `pull_supabase_to_local()` uma vez (`db.py` linhas 261–265), atualizando o cache local.

Resumo prático:

- Fonte imediata da tela: **SQLite local**.
- Supabase influencia indiretamente quando ocorre pull para o local.

---

## 5) O botão **Sincronizar base** poderia ter enviado dados fictícios para o Supabase?

**SIM, poderia.**

Evidências:

- Botão **Sincronizar base** (`ui/app.py` linha 196) chama `push_to_supabase()` (`ui/app.py` linhas 1378+).
- `push_to_supabase()` executa `sync_local_to_supabase()` (`ui/app.py` linha 1384).
- `sync_local_to_supabase()` envia tabelas locais para Supabase via upsert (`db.py` linhas 692–711), incluindo:
  - `lancamentos`
  - `categorias`
  - demais tabelas

Portanto, se o SQLite local já tinha seed fictício (ou mistura), o botão pode replicar isso para a nuvem.

Observação adicional de risco: além do botão manual, `execute()` também enfileira escritas para nuvem quando Supabase está ativo (`db.py` linhas 592–603).

---

## 6) Diagnóstico consolidado

## Causa provável

Mistura ocorreu porque o projeto traz seed fictício embutido (`config.py` + `init_db()`), e a sincronização pode promover dados locais para o Supabase.

## Origem dos dados fictícios

Origem primária: **código versionado** (`config.py`), aplicado automaticamente por `init_db()` em base local vazia.

Origem secundária no Supabase (quando houver): **sincronização do conteúdo local**.

## Risco para dados reais

- Risco de **contaminação semântica**: categorias/dados de demonstração convivendo com dados pessoais.
- Risco de **propagação bidirecional**:
  - local -> Supabase via sync;
  - Supabase -> local via pull na abertura/recarregar.
- Risco de análises e dashboards ficarem distorcidos por categorias fictícias.

## Plano seguro de correção (sem perda de dados reais)

1. **Congelar sync** até saneamento completo (manter a pausa atual).
2. **Snapshot/backup** completo de SQLite e export do Supabase antes de qualquer limpeza.
3. **Mapear registros fictícios por critérios explícitos** (categorias e meses de seed).
4. **Separar dados reais x fictícios** em relatório de conferência (antes de deletar/editar).
5. **Saneamento controlado**:
   - desativar categorias fictícias não usadas;
   - revisar lançamentos fictícios e remover apenas os confirmados como demo.
6. **Blindagem futura**:
   - remover seed automático em produção/uso real;
   - exigir modo explícito para popular dados demo;
   - bloquear sync quando detectar base “demo”.
7. **Só depois** reabilitar sincronização.

## O que **NÃO** deve ser feito

- Não clicar em **Sincronizar base** durante investigação/saneamento.
- Não rodar sync bidirecional sem backup validado.
- Não apagar categorias/lançamentos em massa sem lista de confirmação.
- Não confiar apenas em nome da categoria para exclusão automática sem revisão humana.
- Não alterar schema/dados diretamente no Supabase em produção sem trilha de auditoria.

---

## Conclusão objetiva

As categorias fictícias investigadas são nativas do seed do projeto (`config.py`) e entram automaticamente no SQLite via `init_db()`.  
A UI lê do SQLite local, e o botão **Sincronizar base** pode sim enviar essa base (incluindo dados fictícios) ao Supabase.

---

## 7) Correção aplicada (branch `hotfix/data-seed-isolation`)

### Mudanças de código

1. **`init_db()` sem auto-seed**
   - Removido seed automático de `CONTAS_RECORRENTES`, `CATEGORIAS_PADRAO` e `DADOS_INICIAIS`.
   - `init_db()` agora cria/migra apenas schema e timestamps.

2. **`seed_demo_data()` explícita**
   - Nova função em `db.py`, **nunca chamada automaticamente**.
   - Insere categorias e lançamentos fictícios com `is_demo=1`.
   - Usa `INSERT OR IGNORE` para não sobrescrever dados reais já existentes.

3. **Proteção na sincronização**
   - `sync_local_to_supabase()` filtra registros demo antes do envio:
     - `is_demo=1` em `lancamentos` / `categorias`;
     - lançamentos que coincidem exatamente com tuplas de `DADOS_INICIAIS`;
     - categorias com nomes claramente fictícios (`CARTOES`) ou perfil idêntico ao seed de `CONTAS_RECORRENTES`.

4. **Fallbacks de produção**
   - `get_categories()` e `get_recurring_categories()` não retornam mais listas fictícias quando o banco está vazio.

5. **Coluna local `is_demo`**
   - Adicionada em `lancamentos` e `categorias` (somente SQLite local; não vai para Supabase).

### O que a correção **não** faz

- Não altera nem apaga dados existentes no SQLite local.
- Não altera dados no Supabase.
- Não executa sincronização.
- Não remove categorias/lançamentos legados já contaminados — saneamento continua manual e controlado.

### Próximo passo recomendado

Após merge do hotfix, revisar base local/Supabase com backup e identificar registros legados sem `is_demo` que ainda precisem de saneamento manual.
