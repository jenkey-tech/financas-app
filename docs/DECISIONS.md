# Decisões técnicas (ADR)

Registro de decisões arquiteturais e de produto inferidas do código atual. Formato inspirado em Architecture Decision Records (ADR).

---

## ADR-001 — Python + Tkinter como stack de UI

**Status:** Aceito  
**Contexto:** App de finanças pessoais para uso local, sem requisito de deploy web.  
**Decisão:** Usar Python stdlib com Tkinter/ttk para interface gráfica.  
**Consequências:**
- Zero dependências de UI externas
- Aparência nativa limitada; customização via estilos ttk
- Dificulta distribuição cross-platform elegante sem empacotamento
- Não há caminho natural para versão mobile/web sem reescrita

---

## ADR-002 — SQLite como única persistência

**Status:** Aceito  
**Contexto:** Dados financeiros pessoais, single-user, volume baixo (centenas a poucos milhares de registros).  
**Decisão:** Arquivo `financas.db` local via `sqlite3` stdlib, sem ORM.  
**Consequências:**
- Simplicidade de setup e backup (copiar arquivo)
- Migrações ad hoc via `ALTER TABLE` + try/except em `init_db()`
- Sem concorrência multi-processo
- Dados versionados no Git junto com código (decisão operacional do usuário)

---

## ADR-003 — Unicidade (mes, categoria) em lançamentos

**Status:** Aceito  
**Contexto:** Controle mensal por categoria de despesa (uma fatura de cartão por mês, uma conta de luz, etc.).  
**Decisão:** Constraint `UNIQUE(mes, categoria)` na tabela `lancamentos`.  
**Consequências:**
- Modelo alinhado ao checklist mensal
- Múltiplos lançamentos parciais exigem **soma** (categorias acumulativas) ou substituição explícita
- Não suporta duas contas distintas com mesmo nome no mesmo mês

---

## ADR-004 — Categorias acumulativas vs fixas

**Status:** Aceito  
**Contexto:** Cartões e consumo variável recebem múltiplos lançamentos; aluguel/escola são valores únicos.  
**Decisão:** Conjuntos `CATEGORIAS_ACUMULATIVAS` e `CATEGORIAS_FIXAS` em `config.py` governam comportamento em duplicatas.  
**Consequências:**
- UX diferenciada sem schema extra
- Lista hardcoded; novas categorias seguem regra "fixa" (dialog) por padrão
- Gerenciador de categorias no banco não altera automaticamente esses conjuntos

---

## ADR-005 — Matplotlib opcional com fallback canvas

**Status:** Aceito  
**Contexto:** Gráficos melhoram insights, mas app deve abrir sem pip install extra.  
**Decisão:** `try/import matplotlib`; flag `HAS_MATPLOTLIB`; fallback para `tk.Canvas` com texto/barras simples.  
**Consequências:**
- Degradação graciosa
- Dois caminhos de renderização para manter (matplotlib + canvas)

---

## ADR-006 — Refatoração modular incompleta (v1.5.0+)

**Status:** Aceito (estado atual)  
**Contexto:** `financas_app.py` monolítico difícil de manter; necessidade de separar responsabilidades.  
**Decisão:** Criar `config.py`, `db.py`, `utils.py`, `ui/app.py`, `services/`; manter `financas_app.py` como ponte para `main.py`.  
**Consequências:**
- Estrutura de pastas modular, mas **lógica ainda concentrada em `ui/app.py`**
- `services/` contém apenas re-exports (refatoração pendente)
- Compatibilidade preservada: `python financas_app.py` continua funcionando

---

## ADR-007 — Versionamento histórico em pastas no repositório

**Status:** Aceito (legado)  
**Contexto:** Evolução iterativa com snapshots zip/pasta por versão (v1.4.0 … v1.6.1).  
**Decisão:** Manter cada versão em subpasta `financas_app_vX.Y.Z/` dentro do mesmo repo Git.  
**Consequências:**
- Histórico acessível sem tags Git
- Repositório inflado (múltiplos `.db`, backups, zips removidos em commits recentes)
- Confusão sobre qual pasta é a "oficial" — resolvida documentalmente: **v1.6.1**

**Revisão futura:** migrar histórico para tags Git e limpar raiz (ver ROADMAP Fase 0).

---

## ADR-008 — Integração Git via subprocess na UI

**Status:** Aceito  
**Contexto:** Usuário quer versionar estado financeiro no GitHub sem linha de comando.  
**Decisão:** Botão "Commit estado atual" executa `git add .` + `git commit -m "dados {timestamp}"`; push manual.  
**Consequências:**
- Backup único rotativo: `backups/estado_anterior.db` + botão "Restaurar anterior"
- Export CSV automático em cada commit via UI
- Depende de Git instalado e repo inicializado
- Commits podem incluir arquivos não relacionados se houver mudanças pendentes

---

## ADR-009 — Pendências ignoradas sem alterar lançamentos

**Status:** Aceito  
**Contexto:** Contas regularizadas fora do app ou falsos positivos na lista de vencidos.  
**Decisão:** Tabela `pendencias_ignoradas` oculta item em "Próximos gastos" sem modificar `lancamentos`.  
**Consequências:**
- Ação reversível apenas removendo registro (sem UI de desfazer hoje)
- Backup antes de ignorar (`backup_database("antes_ignorar_pendencia")`)

---

## ADR-010 — Dados iniciais hardcoded

**Status:** Aceito  
**Contexto:** Primeira execução com banco vazio deve demonstrar funcionalidades.  
**Decisão:** `DADOS_INICIAIS` em `config.py` popula lançamentos 2025-01 a 2026-04 se `COUNT(lancamentos) = 0`.  
**Consequências:**
- Seed específico do domínio financeiro do autor
- Novos usuários herdam dados de exemplo (podem apagar/importar CSV)

---

## ADR-011 — Formato CSV brasileiro

**Status:** Aceito  
**Decisão:** Delimitador `;`, encoding `utf-8-sig`, colunas `mes;categoria;valor;status_lancamento;observacao`.  
**Consequências:** Compatível com Excel pt-BR; import usa `INSERT OR REPLACE`.

---

## ADR-012 — Agrupamento "Cartões" nos gráficos

**Status:** Aceito (v1.6.0+)  
**Contexto:** Quatro cartões separados distorcem gráfico de pizza.  
**Decisão:** `normalize_chart_category()` agrupa `CARTOES` como "Cartões" em insights; filtro dedicado "Cartões".  
**Consequências:** Consistência visual; detalhe por cartão exige filtro de categoria individual.

---

## Template para novas decisões

```markdown
## ADR-XXX — Título

**Status:** Proposto | Aceito | Substituído | Depreciado
**Contexto:** ...
**Decisão:** ...
**Consequências:** ...
```
