# Roadmap — App de Finanças Pessoais

Roadmap derivado do estado atual do código (v1.6.1) e das lacunas arquiteturais identificadas. Itens ordenados por prioridade sugerida, **sem estimativas de calendário**.

---

## Fase 0 — Consolidação da base (pré-refatoração)

Objetivo: tornar `financas_app_v1.6.1/` a estrutura oficial na raiz do repositório.

- [ ] Promover conteúdo de `financas_app_v1.6.1/` para a raiz do repositório
- [ ] Arquivar ou remover snapshots `financas_app_v1.4.x`–`v1.5.x` (ou mover para branch/tag Git)
- [ ] Unificar README raiz com versão e instruções de `v1.6.1`
- [ ] Definir política de versionamento semântico (resolver discrepância v1.6.1 vs "v5" legado)
- [ ] Adicionar `.gitignore` na raiz (excluir `__pycache__`, opcionalmente `backups/` ruidosos)

**Critério de conclusão:** um único ponto de entrada na raiz, documentação alinhada, histórico preservado em tags.

---

## Fase 1 — Qualidade e manutenibilidade

Objetivo: reduzir risco antes de novas funcionalidades.

- [ ] Extrair lógica de negócio de `ui/app.py` para `services/financeiro.py` e `services/insights.py`
- [ ] Criar testes unitários para `utils.py`, `status_pagamento`, `parse_valor`, projeção mensal
- [ ] Testes de integração para `init_db()` e migrações de schema
- [ ] Introduzir camada de repositório (`repositories/lancamentos.py`) separando SQL da UI
- [ ] Linting/formatting (ruff ou black + isort)
- [ ] CI mínimo: `python -m compileall` + testes em push/PR

**Critério de conclusão:** `ui/app.py` abaixo de ~800 linhas; cobertura dos fluxos críticos de negócio.

---

## Fase 2 — Experiência do usuário

Objetivo: melhorias incrementais sem mudar o modelo de dados.

- [ ] Atalhos de teclado (Salvar, Mês vigente, Usar sugestão)
- [ ] Busca/filtro por categoria na listagem de lançamentos (reintroduzir tabela ou painel lateral)
- [ ] Exportação de receitas e metas em CSV (hoje só lançamentos)
- [ ] Importação de receitas via CSV
- [ ] Indicador visual de progresso das metas (barra na treeview)
- [ ] Tema escuro opcional
- [ ] Lembrete visual para contas vencidas no título da janela

---

## Fase 3 — Dados e persistência

Objetivo: robustez do armazenamento local.

- [ ] Sistema formal de migrações SQLite (version table + scripts incrementais)
- [ ] Separar dados de usuário do repositório Git (`.gitignore` para `financas.db`, manter export/backup manual)
- [ ] Backup automático na abertura do app (rotação: manter últimos N)
- [ ] Validação de integridade referencial (categoria em lançamento existe no catálogo)
- [ ] Suporte a múltiplos perfis/carteiras (novo schema)

---

## Fase 4 — Funcionalidades financeiras

Objetivo: expandir capacidades analíticas.

- [ ] Orçamento mensal por categoria (teto vs realizado)
- [ ] Comparativo mês a mês (% variação por categoria)
- [ ] Alertas configuráveis (ex.: cartão > X% da renda)
- [ ] Parcelas e recorrências com data fim
- [ ] Tags ou subcategorias
- [ ] Dashboard anual consolidado
- [ ] Export PDF de relatório mensal

---

## Fase 5 — Distribuição (opcional)

Objetivo: facilitar instalação fora do ambiente de desenvolvimento.

- [ ] Empacotamento com PyInstaller ou cx_Freeze (executável Windows/Linux)
- [ ] Script de instalação de dependências para usuários não técnicos
- [ ] Verificação de versão mínima do Python no startup

---

## Fora de escopo (por decisão implícita do projeto atual)

- Backend cloud / sincronização multi-dispositivo
- App mobile nativo
- Integração bancária Open Finance
- Multiusuário com autenticação
- Substituir Tkinter por framework web (Next.js, etc.) — seria reescrita, não evolução

---

## Como priorizar

1. **Fase 0** desbloqueia manutenção limpa
2. **Fase 1** reduz custo de cada feature futura
3. Fases 2–4 podem ser intercaladas conforme necessidade do usuário final
4. Fase 5 só após base estável e testada

Atualizar este roadmap a cada release significativa. Registrar decisões estruturais em [DECISIONS.md](./DECISIONS.md).
