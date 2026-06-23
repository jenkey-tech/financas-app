# Changelog

Histórico consolidado do App de Finanças Pessoais, baseado nos changelogs das versões preservadas no repositório e no código em `financas_app_v1.6.1/`.

Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [Unreleased]

### Added
- Documentação oficial em `docs/` (AI_CONTEXT, ARCHITECTURE, ROADMAP, DECISIONS, CHANGELOG, SETUP_DESENVOLVIMENTO)

---

## [1.6.1] — 2026-06-12

### Changed
- Cards superiores da aba Lançamentos: total do mês, já pago (verde), falta pagar (vermelho)
- Seção de vencimentos renomeada para **Próximos gastos** com total em aberto
- Removida tabela inferior de lançamentos da aba principal (edição via pagamentos + formulário)

### Fixed
- Correções de lançamentos reportadas no commit `fix lancamentos v1.6.1`

---

## [1.6.0] — 2026-06-12

### Added
- Botão **Restaurar anterior** (restaura `backups/estado_anterior.db`)
- Commit de estado salva apenas o último backup rotativo (não histórico ilimitado)
- Filtro de gráficos por categoria (inclui agrupamento "Cartões")
- Janela de **Análise detalhada** com heurísticas de saúde financeira
- Gráfico de saúde financeira (receitas vs despesas vs saldo)

### Changed
- Gráficos redesenhados para telas menores
- Top gastos: gráfico de **pizza** (cartões agrupados)
- Evolução mensal respeita período e categoria selecionados
- Insights resumidos por padrão; detalhe em janela separada

### Removed
- Gráfico "Cartões x Fixos"

---

## [1.5.2] — 2026-06-12

### Fixed
- Hotfix de inicialização após refatoração modular
- Tela de pagamentos usa `get_recurring_categories()` do banco

---

## [1.5.1] — 2026-06-12

### Added
- Botão **Commit estado atual** (substitui Backup e Backup + Git)
- Commit local Git com snapshot CSV; push continua manual

### Removed
- Botões separados de Backup e Backup + Git

---

## [1.5.0] — 2026-06-12

### Added
- Refatoração estrutural em módulos: `config.py`, `db.py`, `utils.py`, `ui/app.py`, `services/`
- Ponte de compatibilidade `financas_app.py` → `main.py`
- Tabelas `receitas`, `metas`, `categorias`, `pendencias_ignoradas`
- Abas Fluxo de caixa e Metas
- Gerenciador de categorias
- Backups automáticos antes de operações sensíveis

### Changed
- Categorias recorrentes migradas para tabela `categorias`

---

## [1.4.1] — 2026-06-12

### Changed
- Redesign visual da aba Lançamentos
- Cards de resumo compactados
- Filtro de mês e formulário lado a lado
- Controle de pagamentos e vencimentos lado a lado
- Hierarquia visual nos botões de ação

---

## [1.4.0] — 2026-06-12

### Added
- Interface de lançamentos reorganizada
- Gerenciador de categorias (modal)
- Regularização/ignore de pendências vencidas e próximas
- Insights por mês, intervalo ou todos os meses
- Gráficos e análise de saúde financeira por período

---

## [1.3.0]

### Added
- Categorias configuráveis no banco
- Vencimentos e recorrência por categoria

---

## [1.2.0]

### Added
- Projeções mensais de gastos
- Gráficos Matplotlib
- Melhorias na aba Insights

---

## [1.1.0]

### Added
- Controle de pagamentos e vencimentos
- Status colorido (Pago, Não pago, Vencido, Débito automático)
- Sugestão automática de valor baseada em histórico

---

## [1.0.0]

### Added
- Versão inicial: lançamentos mensais por categoria
- SQLite local, import/export CSV
- Seed de dados históricos

---

## Legado na raiz (`financas_app.py`)

O arquivo monolítico na raiz do repositório (README "v5") representa uma linha paralela simplificada:

- 2 abas (sem Fluxo de caixa, Metas, gerenciador de categorias)
- Schema apenas `lancamentos`
- Gráfico "Cartões x Fixos" (removido na v1.6.0 modular)
- Sem integração Git na UI

**Não evoluir esta cópia** — usar `financas_app_v1.6.1/` como referência.

---

[Unreleased]: https://github.com/jenkey-tech/financas-app/compare/main...HEAD
[1.6.1]: https://github.com/jenkey-tech/financas-app/commit/da9264b
[1.6.0]: https://github.com/jenkey-tech/financas-app
[1.5.2]: https://github.com/jenkey-tech/financas-app
[1.5.1]: https://github.com/jenkey-tech/financas-app
[1.5.0]: https://github.com/jenkey-tech/financas-app
[1.4.1]: https://github.com/jenkey-tech/financas-app
[1.4.0]: https://github.com/jenkey-tech/financas-app
