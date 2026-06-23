# Roadmap — Finanças App

> Direção proposta a partir da base **v3.4.3**. Itens ordenados por impacto e dependência.  
> Este documento não representa compromisso de prazo — serve como guia de evolução.

## Estado atual (v3.4.3)

Base oficial reiniciada no GitHub com:

- App desktop funcional (5 abas)
- SQLite local + sync Supabase opcional
- Dashboard, insights, metas, fluxo de caixa
- Documentação em `docs/`

---

## Fase 1 — Estabilização e higiene de código

Objetivo: reduzir dívida técnica sem alterar comportamento visível.

| Item | Descrição | Prioridade |
|------|-----------|------------|
| Extrair módulos de `ui/app.py` | Dividir por aba (dashboard, lançamentos, insights) | Alta |
| Extrair lógica de insights | Mover projeções e métricas para módulo dedicado | Média |
| Testes unitários mínimos | Cobrir `utils.py`, `status_pagamento`, `parse_valor` | Média |
| Lint/format | Adicionar `ruff` com CI básico | Baixa |

---

## Fase 2 — Experiência do usuário

Objetivo: melhorias incrementais na interface e fluxos.

| Item | Descrição |
|------|-----------|
| Atalhos de teclado | Salvar (Ctrl+S), navegar meses, foco em campos |
| Busca/filtro de categorias | Em listas longas de lançamentos |
| Reativar import/export CSV | Via menu ou aba Configurações |
| Notificações de vencimento | Lembrete local (opcional, sem cloud) |
| Tema escuro | Complementar ao ttkbootstrap flatly |
| Responsividade | Melhor adaptação em telas menores que 1100px |

---

## Fase 3 — Dados e sincronização

Objetivo: tornar o sync mais robusto e previsível.

| Item | Descrição |
|------|-----------|
| Indicador de fila cloud | Mostrar envios pendentes / erros recentes na UI |
| Retry com backoff | Reenvio automático de writes falhos na fila |
| Resolução de conflitos | Estratégia explícita quando `updated_at` diverge |
| Autenticação Supabase | Login por usuário + RLS para uso compartilhado |
| Migrações versionadas | Substituir ALTER TABLE ad-hoc por schema version table |

---

## Fase 4 — Análise financeira

Objetivo: aprofundar o valor do módulo de insights.

| Item | Descrição |
|------|-----------|
| Orçamento por categoria | Limite mensal + alerta ao ultrapassar |
| Comparativo mês a mês | Variação percentual por categoria |
| Export PDF | Relatório mensal para arquivo |
| Metas vinculadas a lançamentos | Progresso automático ao registrar pagamentos |
| Previsão de fluxo de caixa | Projeção 3–6 meses com base em recorrentes |

---

## Fase 5 — Distribuição (longo prazo)

Objetivo: facilitar instalação fora do ambiente de desenvolvimento.

| Item | Descrição |
|------|-----------|
| Empacotamento PyInstaller | Executável Windows sem Python instalado |
| Instalador | MSI ou script de setup |
| Atualização automática | Verificação de release no GitHub |
| Versão web (avaliar) | PWA ou app Supabase — decisão arquitetural maior |

---

## Critérios de priorização

1. **Não quebrar modo offline** — SQLite deve continuar funcionando sem `.env`
2. **Mudanças pequenas e revisáveis** — preferir PRs focados
3. **Documentar decisões** — registrar em [DECISIONS.md](./DECISIONS.md)
4. **Hotfixes antes de features** — estabilidade da sync e pagamentos primeiro

---

## Fora de escopo (por enquanto)

- Multi-moeda
- Integração bancária Open Finance
- App mobile nativo
- Contabilidade formal / nota fiscal

---

## Como contribuir com o roadmap

1. Abra issue descrevendo problema ou melhoria
2. Referencie fase e item deste documento
3. Para mudanças arquiteturais, adicione entrada em `DECISIONS.md` antes ou junto do PR
