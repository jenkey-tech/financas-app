# App de Finanças Pessoais

Versão atual: **v1.5.0**

## Como rodar

```bash
python financas_app.py
```

ou:

```bash
python main.py
```

## Instalar dependências

```bash
pip install -r requirements.txt
```

## Estrutura refatorada

```text
financas-app/
├── main.py
├── financas_app.py
├── config.py
├── db.py
├── utils.py
├── services/
│   ├── categorias.py
│   ├── backups.py
│   └── financeiro.py
├── ui/
│   └── app.py
├── financas.db
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

## Observação

O arquivo `financas_app.py` foi mantido como ponte de compatibilidade.
Isso permite continuar rodando o app do jeito antigo.


## v1.5.1

- Removidos botões separados de Backup e Backup + Git.
- Adicionado botão único **Commit estado atual**.
- O botão gera snapshot CSV e cria commit local no Git.
- O push para GitHub continua manual, via GitHub Desktop ou `git push`.


## v1.5.2

- Correção de inicialização após refatoração.
- Corrigida referência a `CONTAS_RECORRENTES` na tela de pagamentos.


## v1.6.0

- Botão **Commit estado atual** agora salva somente o último estado anterior do banco.
- Novo botão **Restaurar anterior** restaura esse último estado salvo.
- Gráficos de insights redesenhados para caber melhor na tela.
- Gráfico de evolução dos gastos totais por mês.
- Top gastos do período agora em gráfico de pizza.
- Cartões são agrupados como uma única categoria nos gráficos.
- Removido gráfico Cartões x Fixos.
- Filtro de gráficos por categoria específica.
- Insights resumidos por padrão, com botão para análise detalhada.


## v1.6.1

- Cards superiores da aba Lançamentos agora mostram:
  - total do mês;
  - já pago em verde;
  - falta pagar em vermelho.
- Seção de vencidos/próximos 7 dias renomeada para **Próximos gastos**.
- Próximos gastos agora mostra o total em aberto.
- Removida a tabela inferior de lançamentos da aba principal.
