# Plano de limpeza segura do cache SQLite local

> **Status:** análise e proposta apenas — **nenhuma limpeza executada**.  
> **Data:** 2026-07-08  
> **Contexto:** contaminação por seed fictício legado (`init_db()` antigo) + risco de sync para Supabase.

---

## 1) Caminho do SQLite local usado pelo app

### Definição no código

- Constante: `DB_FILE = "financas.db"` em `config.py`
- Resolução: caminho **relativo ao diretório de trabalho atual (CWD)** ao executar `python main.py`
- Funções: `db.db_path()` e `sqlite3.connect(DB_FILE)` em `db.py`

### Caminhos esperados

| Ambiente | Caminho provável |
|----------|------------------|
| Repositório (raiz do projeto) | `./financas.db` |
| Windows (sua instalação citada) | `C:\Users\gston\OneDrive\Área de Trabalho\financas-app\financas_app_v3.5.0\financas.db` |
| Backups automáticos do app | `./backups/financas_<motivo>_<timestamp>.db` |

### Observação desta investigação

No ambiente cloud do repositório, **não há `financas.db` versionado nem presente em disco** (arquivo gitignored).  
A auditoria abaixo usa critérios do código; a execução dos comandos deve ser feita **no seu ambiente local Windows**.

---

## 2) Origem provável da contaminação

1. **Seed automático legado** (antes do hotfix `ab344fb`):
   - `init_db()` inseria `CONTAS_RECORRENTES` e `CATEGORIAS_PADRAO` em `categorias`
   - Se `lancamentos` estivesse vazio, inseria `DADOS_INICIAIS`
2. **Fallback fictício na UI/DB** (versões antigas):
   - `get_categories()` e `get_recurring_categories()` podiam expor listas demo mesmo sem dados reais
3. **Sincronização manual** (se já ocorreu no passado):
   - botão **Sincronizar base** podia enviar cache local contaminado ao Supabase
   - pull na abertura podia trazer de volta dados misturados

**Hotfix já mergeado na `main`:** auto-seed removido; `seed_demo_data()` só manual; sync bloqueia `is_demo=1` e padrões conhecidos.

---

## 3) Critérios de classificação dos suspeitos

### A) Claramente fictícios (alta confiança)

| Tipo | Critério |
|------|----------|
| Lançamento | `is_demo = 1` |
| Lançamento | tupla exata `(mes, categoria, valor)` em `DADOS_INICIAIS` |
| Categoria | `is_demo = 1` |
| Categoria | nome em `CARTOES` (Cartão Alpha, Cartão Beta dia 08, Cartão Beta dia 15, Cartão Loja Online) |
| Categoria | perfil idêntico ao seed de `CONTAS_RECORRENTES` (nome + dia + tipo + recorrente=1 + ativa=1) |

### B) Possivelmente reais (revisão humana obrigatória)

| Tipo | Critério |
|------|----------|
| Categoria | nome genérico do portfólio demo (`Escola`, `Creche`, `IPTU`, `Aluguel`, etc.) **sem** `is_demo=1` e com valores/datas diferentes do seed |
| Lançamento | categoria genérica com valor diferente dos 20 registros de `DADOS_INICIAIS` |
| Categoria | criada manualmente pelo usuário com mesmo nome de demo, porém com regra diferente (dia/tipo/recorrente) |

### C) Reais (preservar)

| Tipo | Critério |
|------|----------|
| Categoria/Lançamento | não casa com critérios A |
| Categoria/Lançamento | `is_demo = 0` e diverge do perfil demo |
| Qualquer registro | categorias personalizadas fora das listas demo (`config.py`) |

---

## 4) Itens suspeitos conhecidos (catálogo do seed)

### Categorias do seed legado (`CATEGORIAS_PADRAO` / `CONTAS_RECORRENTES`)

**Claramente fictícias (nomes exclusivos de demo):**
- Cartão Alpha
- Cartão Beta dia 08
- Cartão Beta dia 15
- Cartão Loja Online

**Genéricas (podem ser reais — revisar caso a caso):**
- Água, Energia, Gás, Internet, Aluguel, Escola, Creche, Diarista, Condomínio, IPTU, Delivery, Parcela Móveis, Contador, Empréstimo

### Lançamentos seed (`DADOS_INICIAIS`) — todos claramente fictícios se idênticos

| mes | categoria | valor |
|-----|-----------|------:|
| 2025-01 | Cartão Alpha | 850.00 |
| 2025-01 | Cartão Beta dia 15 | 1200.00 |
| 2025-01 | Energia | 180.50 |
| 2025-01 | Gás | 45.00 |
| 2025-01 | Internet | 99.90 |
| 2025-01 | Aluguel | 2200.00 |
| 2025-01 | Escola | 1500.00 |
| 2025-01 | Condomínio | 650.00 |
| 2025-02 | Cartão Alpha | 920.00 |
| 2025-02 | Cartão Beta dia 15 | 980.00 |
| 2025-02 | Energia | 165.00 |
| 2025-02 | Internet | 99.90 |
| 2025-02 | Aluguel | 2200.00 |
| 2025-02 | Escola | 1500.00 |
| 2025-02 | Delivery | 120.00 |
| 2025-03 | Cartão Alpha | 780.00 |
| 2025-03 | Energia | 190.00 |
| 2025-03 | Aluguel | 2200.00 |
| 2025-03 | Escola | 1500.00 |
| 2025-03 | Delivery | 95.00 |

---

## 5) Backup obrigatório (antes de qualquer limpeza)

> **Regra:** não executar DELETE/UPDATE destrutivo sem backup validado.

### Opção A — via app (recomendada)

No diretório do projeto local:

```powershell
cd "C:\Users\gston\OneDrive\Área de Trabalho\financas-app\financas_app_v3.5.0"
python -c "from db import backup_database; print(backup_database('antes_limpeza_cache'))"
```

### Opção B — cópia manual do arquivo

```powershell
$src = "C:\Users\gston\OneDrive\Área de Trabalho\financas-app\financas_app_v3.5.0\financas.db"
$dst = "C:\Users\gston\OneDrive\Área de Trabalho\financas-app\financas_app_v3.5.0\backups\financas_antes_limpeza_manual.db"
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
Copy-Item $src $dst
```

### Validação do backup

```powershell
python -c "import sqlite3; c=sqlite3.connect(r'backups\financas_antes_limpeza_manual.db'); print('lancamentos', c.execute('select count(*) from lancamentos').fetchone()[0]); print('categorias', c.execute('select count(*) from categorias').fetchone()[0])"
```

**Status nesta investigação cloud:** backup físico **não criado aqui** (arquivo local ausente no ambiente remoto).

---

## 6) Auditoria read-only (executar no ambiente local)

### 6.1 Verificar coluna `is_demo` (pós-hotfix)

```sql
PRAGMA table_info(categorias);
PRAGMA table_info(lancamentos);
```

Se `is_demo` não existir, abrir o app uma vez com versão hotfix (`init_db()` migra schema sem inserir demo).

### 6.2 Listar categorias claramente fictícias

```sql
SELECT nome, dia_vencimento, tipo, recorrente, ativa, COALESCE(is_demo,0) AS is_demo
FROM categorias
WHERE COALESCE(is_demo,0)=1
   OR nome IN ('Cartão Alpha','Cartão Beta dia 08','Cartão Beta dia 15','Cartão Loja Online')
ORDER BY nome;
```

### 6.3 Listar lançamentos claramente fictícios

```sql
SELECT mes, categoria, valor, status_lancamento, COALESCE(is_demo,0) AS is_demo
FROM lancamentos
WHERE COALESCE(is_demo,0)=1
   OR (mes='2025-01' AND categoria='Cartão Alpha' AND valor=850.00)
   OR (mes='2025-01' AND categoria='Cartão Beta dia 15' AND valor=1200.00)
   OR (mes='2025-01' AND categoria='Energia' AND valor=180.50)
   OR (mes='2025-01' AND categoria='Gás' AND valor=45.00)
   OR (mes='2025-01' AND categoria='Internet' AND valor=99.90)
   OR (mes='2025-01' AND categoria='Aluguel' AND valor=2200.00)
   OR (mes='2025-01' AND categoria='Escola' AND valor=1500.00)
   OR (mes='2025-01' AND categoria='Condomínio' AND valor=650.00)
   OR (mes='2025-02' AND categoria='Cartão Alpha' AND valor=920.00)
   OR (mes='2025-02' AND categoria='Cartão Beta dia 15' AND valor=980.00)
   OR (mes='2025-02' AND categoria='Energia' AND valor=165.00)
   OR (mes='2025-02' AND categoria='Internet' AND valor=99.90)
   OR (mes='2025-02' AND categoria='Aluguel' AND valor=2200.00)
   OR (mes='2025-02' AND categoria='Escola' AND valor=1500.00)
   OR (mes='2025-02' AND categoria='Delivery' AND valor=120.00)
   OR (mes='2025-03' AND categoria='Cartão Alpha' AND valor=780.00)
   OR (mes='2025-03' AND categoria='Energia' AND valor=190.00)
   OR (mes='2025-03' AND categoria='Aluguel' AND valor=2200.00)
   OR (mes='2025-03' AND categoria='Escola' AND valor=1500.00)
   OR (mes='2025-03' AND categoria='Delivery' AND valor=95.00)
ORDER BY mes, categoria;
```

### 6.4 Listar suspeitos “possivelmente reais” (revisão manual)

```sql
-- Categorias com nomes genéricos do seed, mas sem marca is_demo
SELECT nome, dia_vencimento, tipo, recorrente, ativa, COALESCE(is_demo,0) AS is_demo
FROM categorias
WHERE nome IN (
  'Água','Energia','Gás','Internet','Aluguel','Escola','Creche','Diarista',
  'Condomínio','IPTU','Delivery','Parcela Móveis','Contador','Empréstimo'
)
AND COALESCE(is_demo,0)=0
ORDER BY nome;

-- Lançamentos dessas categorias fora das tuplas exatas de DADOS_INICIAIS
SELECT l.mes, l.categoria, l.valor, l.status_lancamento
FROM lancamentos l
WHERE l.categoria IN (
  'Água','Energia','Gás','Internet','Aluguel','Escola','Creche','Diarista',
  'Condomínio','IPTU','Delivery','Parcela Móveis','Contador','Empréstimo'
)
AND COALESCE(l.is_demo,0)=0
ORDER BY l.mes, l.categoria;
```

### 6.5 Export de conferência (sem alterar dados)

```powershell
python -c "from db import export_snapshot_csv; print(export_snapshot_csv())"
```

---

## 7) Plano seguro de limpeza (NÃO executar ainda)

### Princípios

1. **Não usar DELETE em massa** na primeira rodada.
2. Tratar primeiro o grupo **claramente fictício**.
3. Para categorias genéricas (`Escola`, `IPTU`, etc.), decidir manualmente.
4. **Não clicar em Sincronizar base** durante saneamento.
5. **Não alterar Supabase** nesta etapa.

### Fase 1 — neutralizar (baixo risco)

Desativar categorias claramente fictícias (preserva histórico, não apaga):

```sql
-- Executar SOMENTE após backup validado
UPDATE categorias
SET ativa = 0
WHERE COALESCE(is_demo,0)=1
   OR nome IN ('Cartão Alpha','Cartão Beta dia 08','Cartão Beta dia 15','Cartão Loja Online');
```

### Fase 2 — remover lançamentos claramente fictícios (revisar SELECT antes)

```sql
-- 2.1 Conferência
SELECT id, mes, categoria, valor, COALESCE(is_demo,0) AS is_demo
FROM lancamentos
WHERE COALESCE(is_demo,0)=1
   OR (mes, categoria, ROUND(valor,2)) IN (
        ('2025-01','Cartão Alpha',850.00),
        ('2025-01','Cartão Beta dia 15',1200.00),
        ('2025-01','Energia',180.50),
        ('2025-01','Gás',45.00),
        ('2025-01','Internet',99.90),
        ('2025-01','Aluguel',2200.00),
        ('2025-01','Escola',1500.00),
        ('2025-01','Condomínio',650.00),
        ('2025-02','Cartão Alpha',920.00),
        ('2025-02','Cartão Beta dia 15',980.00),
        ('2025-02','Energia',165.00),
        ('2025-02','Internet',99.90),
        ('2025-02','Aluguel',2200.00),
        ('2025-02','Escola',1500.00),
        ('2025-02','Delivery',120.00),
        ('2025-03','Cartão Alpha',780.00),
        ('2025-03','Energia',190.00),
        ('2025-03','Aluguel',2200.00),
        ('2025-03','Escola',1500.00),
        ('2025-03','Delivery',95.00)
   );

-- 2.2 Remoção pontual (somente IDs retornados na conferência)
-- DELETE FROM lancamentos WHERE id IN (...);
```

### Fase 3 — revisão manual de “possivelmente reais”

Para cada categoria genérica:

- se for despesa real sua → **manter**
- se for resquício de demo sem uso → desativar categoria (`ativa=0`) e remover lançamentos associados **apenas após confirmação**

### Fase 4 — pendências e integridade

```sql
SELECT * FROM pendencias_ignoradas
WHERE categoria IN ('Cartão Alpha','Cartão Beta dia 08','Cartão Beta dia 15','Cartão Loja Online');

-- Remover pendências apenas das categorias confirmadas como fictícias
-- DELETE FROM pendencias_ignoradas WHERE id IN (...);
```

---

## 8) Validação pós-limpeza (antes de reabrir sync)

1. Abrir app (`python main.py`) **sem** Supabase sync manual.
2. Conferir abas:
   - **Lançamentos:** categorias reais aparecem; fictícias não aparecem (ou aparecem desativadas).
   - **Dashboard/Insights:** totais coerentes com histórico real.
3. Rodar auditoria SQL:
   ```sql
   SELECT COUNT(*) FROM lancamentos WHERE COALESCE(is_demo,0)=1;
   SELECT COUNT(*) FROM categorias WHERE COALESCE(is_demo,0)=1 AND ativa=1;
   ```
   Esperado: `0` para dados demo removidos/desativados.
4. Exportar CSV de conferência (`export_snapshot_csv()`).
5. **Somente após validação humana**, considerar sync (fora deste plano).

---

## 9) Rollback

Se algo sair errado:

### Opção 1 — restaurar backup

```powershell
$backup = "backups\financas_antes_limpeza_manual.db"   # ou arquivo gerado por backup_database
Copy-Item $backup "financas.db" -Force
```

### Opção 2 — restaurar pelo app

Se existir `backups/estado_anterior.db`, usar botão **Restaurar anterior** na UI.

### Pós-rollback

1. Reabrir app e validar totais.
2. Reexecutar queries da seção 6.
3. Replanejar limpeza em lote menor (por categoria/mês).

---

## 10) Resumo executivo

| Grupo | Ação recomendada |
|-------|------------------|
| Claramente fictícios (`CARTOES`, `is_demo=1`, tuplas `DADOS_INICIAIS`) | desativar/remover após backup |
| Possivelmente reais (nomes genéricos) | revisão manual obrigatória |
| Reais (fora dos padrões demo) | **preservar** |

**Risco residual:** dados genéricos (`Escola`, `IPTU`, etc.) podem ser reais e não devem ser apagados automaticamente.

**Próximo passo sugerido:** executar auditoria read-only (seção 6) no caminho Windows local e colar os resultados para aprovação da Fase 1/2.
