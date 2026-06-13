# App de Finanças Pessoais v6

## Como rodar

```bash
python financas_app.py
```

## Dependência recomendada

```bash
pip install -r requirements.txt
```

## Novidades da v6

- Backup automático do `financas.db` ao abrir o app e antes de salvar/excluir/importar dados.
- Botão **Backup** para criar cópia local do banco e exportação CSV.
- Botão **Backup + Git** para criar backup, fazer commit curto `backup` e executar `git push`.
- Painel **Próximos 7 dias** na aba Lançamentos.
- Nova aba **Fluxo de caixa** para cadastrar receitas e ver saldo projetado.
- Nova aba **Metas** para acompanhar objetivos financeiros.
- Insights agora consideram receitas, despesas e saldo projetado.

## Observação

O arquivo `financas.db` foi mantido no pacote para preservar os dados já imputados no app. Antes de substituir arquivos no seu computador, faça um commit no GitHub.


## Novidades da v7

- Aba Lançamentos reorganizada: novo lançamento fica acima do controle de pagamentos.
- Botão **Lançar próximo mês** cria o próximo mês com contas recorrentes zeradas.
- Controle de pagamentos agora permite botão direito:
  - editar célula;
  - preencher formulário;
  - deletar lançamento.
- Clique no nome das colunas do controle de pagamentos para ordenar crescente/decrescente.
- Opção **Nova categoria** no formulário.
- Categorias extras lançadas no mês também aparecem no controle de pagamentos.


## Novidades da v8

- Novo menu **Gerenciar categorias** na aba Lançamentos.
- É possível criar, editar, desativar e configurar categoria como:
  - recorrente;
  - somente mês específico.
- Categorias agora podem ter vencimento e tipo:
  - manual;
  - débito automático.
- A lista de vencimentos agora mostra **vencidos e próximos 7 dias**.
- Status **⚠ Não pago vencido** agora aparece com alerta.
- As regras de categoria são salvas no banco `financas.db`, preservando lançamentos antigos.


## v1.4.0

- Reorganização da aba Lançamentos:
  - Gerenciar categorias separado abaixo de Novo/editar lançamento.
  - Lançar próximo mês abaixo de Visualizar mês.
  - Removido Ver todos da aba de lançamentos.
- Vencidos e próximos 7 dias:
  - botão direito permite regularizar/ignorar pendência;
  - pendência ignorada não altera lançamentos já registrados.
- Insights:
  - seleção por mês, intervalo de meses ou Ver todos;
  - análise de saúde financeira baseada em proporções conhecidas de finanças pessoais;
  - novos gráficos por período selecionado.
- Status vencido não pago agora aparece como alerta: ⚠ Não pago vencido.
