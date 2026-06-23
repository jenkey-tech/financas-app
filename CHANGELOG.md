# Changelog

## v3.4.3
- Hotfix: corrigida função ausente `_rows_as_dicts` usada no botão Sincronizar base.


## v3.4.2
- Hotfix: corrigido erro de digitação `_rows_as_discts` no fluxo de sincronização da base.


## v3.4.1
- Hotfix: Próximos gastos agora considera todos os lançamentos Não pagos do mês.
- Hotfix: Dashboard usa a mesma regra de itens em aberto.
- Ajustado gráfico Pago x Em aberto para não ficar cortado.


## v3.4.0
- Corrigida ordenação decrescente dos meses.
- Próximos gastos agora considera todos os itens em aberto do mês vigente.
- Dashboard redesenhado com gráficos e ações recomendadas.
- Insights reformulados para diagnóstico e planejamento financeiro.


## v3.3.0
- Implementado dashboard inicial.
- Adicionado status visual da base/cloud.
- Removidos botões Importar CSV e Exportar CSV do cabeçalho.
- Renomeados botões de Supabase para termos mais claros.
- Corrigida ordenação cronológica de meses.
- Adicionado flush de envios pendentes ao fechar.


## v3.1.0
- Modernização visual da interface.
- Adicionado suporte a `ttkbootstrap`.
- Cabeçalho, cards, botões, abas e tabelas redesenhados.
- Sem alterações na lógica financeira principal.


## v3.0.3
- UX: edição de status agora usa opções fixas clicáveis.
- Removida necessidade de digitar status manualmente.


## v3.0.2
- Corrigida arquitetura cloud para evitar travamentos.
- Dados são puxados do Supabase automaticamente ao abrir.
- Interface usa cache local rápido.
- Alterações seguem para Supabase em segundo plano.
- Botão Recarregar dados força atualização do cache a partir da nuvem.


## v2.1.2
- Hotfix: adicionada definição ausente `SUPABASE_TABLES`.
- Adicionado alias defensivo `supabase_tables`.
- Sincronização manual usa conflitos corretos para lançamentos, categorias e pendências.
- Textos ajustados para deixar claro que alterações sobem em segundo plano.


## v2.1.1
- Patch de performance: gravações no Supabase agora são assíncronas.
- Interface não trava ao editar lançamento.
- Leituras passam a usar cache local para resposta imediata.
- Sincronização manual força envio/recebimento completo.


## v2.1.0
- Cloud-first: Supabase passa a ser a fonte principal quando `.env` está configurado.
- Leituras principais passam a buscar no Supabase.
- Escritas principais passam a salvar direto no Supabase e no cache local.
- SQLite permanece apenas como fallback/cache.
- Botão de sincronização renomeado para Atualizar nuvem.


## v2.0.3
- Hotfix: corrigido erro SQLite `cannot add a column with non-constant default`.
- Migração local agora cria `updated_at` sem default e preenche em seguida.


## v2.0.2
- Hotfix: corrigido erro `no such column: updated_at` na sincronização com Supabase.
- Adicionada migração automática do SQLite local antes do envio.


## v2.0.1
- Incluído `.env` para teste local do Supabase.
- Mantido `.env` no `.gitignore`.
- Mantido `.env.example` genérico.


## v2.0.0
- Mudança major: adicionada arquitetura cloud com Supabase.
- Mantido SQLite local como cache/offline.
- Adicionado `.env.example` para configuração segura.
- Adicionado `sql/supabase_schema.sql`.
- Adicionados botões Testar Supabase e Sincronizar.
- Removido requisito de Turso/libsql.


## v1.7.0
- Adicionado suporte a Turso Cloud via `.env`.
- App usa Turso quando `TURSO_DATABASE_URL` e `TURSO_AUTH_TOKEN` estão configurados.
- Mantido fallback automático para SQLite local.
- Adicionados botões Testar Turso e Migrar p/ Turso.
- Incluído `.env.example`.
- Atualizado `requirements.txt` com `libsql`.


## v1.6.1
- Ajustados cards superiores da aba Lançamentos.
- Adicionado total em aberto em Próximos gastos.
- Renomeada seção de vencimentos para Próximos gastos.
- Removida tabela inferior de lançamentos.


## v1.6.0
- Adicionado ponto único de restauração antes do commit do estado atual.
- Adicionado botão Restaurar anterior.
- Redesenhados gráficos da aba Insights para caberem melhor em telas menores.
- Gráfico de evolução mensal respeita período e categoria selecionados.
- Top gastos agora é gráfico de pizza com cartões agrupados.
- Removido gráfico Cartões x Fixos.
- Insights resumidos com análise detalhada em janela separada.


## v1.5.2
- Hotfix: corrigida falha ao abrir app após refatoração.
- Tela de pagamentos agora usa categorias recorrentes carregadas do banco.


## v1.5.1
- Removidos botões Backup e Backup + Git.
- Adicionado botão Commit estado atual.
- Commit local agora registra o estado atual do banco/exportação sem fazer push automático.


## v1.5.0
- Refatoração estrutural do app em módulos.
- Mantido `financas_app.py` como ponte de compatibilidade.
- Separadas responsabilidades:
  - `config.py`: constantes e configurações;
  - `db.py`: banco, backups e categorias;
  - `utils.py`: formatação, datas e status;
  - `ui/app.py`: interface gráfica;
  - `services/`: serviços de apoio.
- Preservado `financas.db` e compatibilidade com dados existentes.


## v1.4.1
- Redesign visual e layout da aba Lançamentos.
- Cards de resumo compactados.
- Filtro de mês e formulário posicionados lado a lado.
- Controle de pagamentos e vencimentos posicionados lado a lado.
- Botões de ações especiais com hierarquia visual.


## v1.4.0
- Interface de lançamentos reorganizada.
- Gerenciador de categorias separado.
- Regularização/ignore de pendências vencidas e próximas.
- Insights por mês, intervalo ou todos os meses.
- Gráficos e análise de saúde financeira por período.

## v1.3.0
- Categorias configuráveis.
- Vencimentos e recorrência por categoria.

## v1.2.0
- Projeções, gráficos e melhorias de insights.

## v1.1.0
- Controle de pagamentos e vencimentos.

## v1.0.0
- Versão inicial do app.
