# Changelog

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
