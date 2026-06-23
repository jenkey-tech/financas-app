# Setup de desenvolvimento

Guia para configurar o ambiente local e executar o App de Finanças Pessoais (v1.6.1).

---

## Pré-requisitos

| Requisito | Versão mínima | Verificação |
|-----------|---------------|-------------|
| Python | 3.10+ (3.11+ recomendado) | `python --version` ou `python3 --version` |
| Tkinter | Incluso no Python | `python -c "import tkinter"` |
| Git | Qualquer recente | `git --version` (opcional; necessário para botões Git na UI) |
| pip | Qualquer recente | `pip --version` |

### Tkinter no Linux

Em algumas distribuições, Tkinter não vem no pacote base:

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Git

Necessário apenas se for usar **Commit estado atual** / **Restaurar anterior** na interface.

---

## Clone do repositório

```bash
git clone https://github.com/jenkey-tech/financas-app.git
cd financas-app
```

---

## Versão a executar

A versão canônica está em `financas_app_v1.6.1/`:

```bash
cd financas_app_v1.6.1
```

> **Nota:** o `financas_app.py` na raiz do repositório é uma versão legada simplificada. Para desenvolvimento, use sempre a pasta v1.6.1 até a consolidação prevista no ROADMAP.

---

## Ambiente virtual (recomendado)

```bash
cd financas_app_v1.6.1
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

---

## Instalar dependências

```bash
pip install -r requirements.txt
```

Conteúdo atual de `requirements.txt`:

```
matplotlib>=3.8
```

O app **abre sem matplotlib**, mas gráficos da aba Insights ficam simplificados (canvas Tk).

---

## Executar o aplicativo

Qualquer uma das opções:

```bash
python main.py
```

```bash
python financas_app.py
```

A janela abre com título `Finanças Pessoais - v1.6.1`.

---

## Estrutura de arquivos gerados em runtime

| Caminho | Descrição |
|---------|-----------|
| `financas.db` | Banco SQLite principal |
| `backups/` | Backups automáticos e `estado_anterior.db` |
| `exports/` | Snapshots CSV exportados (ex.: ao commitar estado) |

Esses diretórios são criados automaticamente quando necessário.

---

## Primeira execução

1. Se `financas.db` não existir ou estiver vazio, `init_db()` cria o schema e insere:
   - Categorias padrão e contas recorrentes
   - Dados históricos de exemplo (`DADOS_INICIAIS`, 2025-01 a 2026-04)
2. A UI abre no **mês vigente** por padrão
3. Para começar do zero: apague `financas.db` e reinicie (ou importe seu CSV)

---

## Importar / exportar dados

### Exportar

Botão **Exportar CSV** na barra superior → salva todos os lançamentos.

Formato:

```csv
mes;categoria;valor;status_lancamento;observacao
2026-06;Cartão Nubank;1500,00;Pago;
```

### Importar

Botão **Importar CSV** → usa `INSERT OR REPLACE` (sobrescreve mes+categoria existente).

Backup automático: `backups/financas_antes_importar_YYYYMMDD_HHMMSS.db`

---

## Desenvolvimento com Git integrado

A UI oferece:

- **Commit estado atual** — salva `backups/estado_anterior.db`, exporta CSV, executa `git add .` + `git commit`
- **Restaurar anterior** — copia `estado_anterior.db` sobre `financas.db`

Push para GitHub continua **manual**:

```bash
git push origin main
```

---

## Verificação rápida (sem GUI)

Validar imports e schema:

```bash
cd financas_app_v1.6.1
python -c "
from db import init_db, query
init_db()
print('Tabelas OK:', len(query('SELECT name FROM sqlite_master WHERE type=\"table\"')))
"
```

Compilar todos os módulos:

```bash
python -m compileall .
```

---

## Problemas comuns

### `ModuleNotFoundError: No module named 'tkinter'`

Instale o pacote Tkinter do sistema (ver seção Linux acima).

### Gráficos não aparecem / mensagem "Instale matplotlib"

```bash
pip install matplotlib
```

Reinicie o app.

### Janela não abre em ambiente headless (servidor sem display)

Tkinter exige display gráfico. Em CI, limite-se a testes de import/schema. Para Cloud Agents, não execute `mainloop()` sem VNC/X11.

### `Git não encontrado` ao commitar pela UI

Instale Git e garanta que está no `PATH`.

### Banco corrompido ou dados errados

1. Use **Restaurar anterior** se disponível
2. Ou restaure manualmente de `backups/financas_*.db`
3. Ou importe último CSV de `exports/`

---

## Convenções para contribuir

1. Trabalhar a partir de `financas_app_v1.6.1/` até consolidação na raiz
2. Backups automáticos antes de mutações de dados — seguir padrão existente
3. CSV: delimitador `;`, encoding `utf-8-sig`
4. Valores monetários: funções `brl()` e `parse_valor()` de `utils.py`
5. Commits de código: mensagens descritivas em português ou inglês
6. Não versionar backups ruidosos desnecessários (avaliar `.gitignore` na Fase 0 do ROADMAP)

---

## Referências

- [AI_CONTEXT.md](./AI_CONTEXT.md) — contexto para IA
- [ARCHITECTURE.md](./ARCHITECTURE.md) — arquitetura detalhada
- [ROADMAP.md](./ROADMAP.md) — próximos passos
- [DECISIONS.md](./DECISIONS.md) — decisões técnicas
