# Repositório público vs. desenvolvimento privado

Este diretório (`financas-app-public`) é a **versão de portfólio** pronta para publicação no GitHub.

O diretório `financas_app_v3.4.3` (ou um novo repo privado) permanece para **desenvolvimento real**.

## O que mudou na versão pública

| Item | Repo privado (dev) | Repo público (portfólio) |
|------|--------------------|--------------------------|
| Histórico Git | Contém commit com dados reais | Histórico limpo (1 commit) |
| `config.py` | Pode ter categorias reais | Apenas dados fictícios |
| Botão "Commit estado atual" | Presente | **Removido** |
| `services/` | Stubs não usados | **Removido** |
| Código morto (CSV, duplicatas) | Presente | **Removido** |
| `.env` / `financas.db` | Local | Nunca versionados |
| LICENSE | Ausente | MIT |
| README | Changelog longo | Focado em portfólio |

## Publicar no GitHub

### Opção A — Substituir o repo atual (recomendado se já é público)

```powershell
cd "C:\Gui Desenvl\financas-app\financas-app-public"
git remote add origin https://github.com/jenkey-tech/financas-app.git
git push -u origin main --force
```

> **Atenção:** `--force` apaga o histórico remoto antigo (incluindo dados sensíveis). Faça backup do repo privado antes.

### Opção B — Criar repo novo

1. No GitHub: **New repository** → `financas-app` (ou outro nome)
2. Torne o repo antigo **privado** ou renomeie para `financas-app-dev`
3. Push:

```powershell
cd "C:\Gui Desenvl\financas-app\financas-app-public"
git remote add origin https://github.com/jenkey-tech/financas-app.git
git push -u origin main
```

## Manter o repo privado de desenvolvimento

```powershell
# No repo de desenvolvimento (financas_app_v3.4.3)
git remote set-url origin https://github.com/jenkey-tech/financas-app-dev.git
# Ou crie um repo privado novo no GitHub e use essa URL
```

No GitHub: **Settings → General → Danger Zone → Change repository visibility → Private**

## Sincronizar mudanças do privado para o público

Quando uma feature estiver estável no repo privado:

1. Copie apenas os arquivos de código alterados (nunca `.env`, `*.db`, `backups/`, `exports/`)
2. Revise se `config.py` não contém dados reais
3. Commit no repo público

```powershell
# Exemplo: copiar módulos específicos
Copy-Item "..\financas_app_v3.4.3\db.py" ".\db.py"
Copy-Item "..\financas_app_v3.4.3\ui\app.py" ".\ui\app.py"
# Reaplique remoções de portfólio se necessário (sem botão Git, sem dados reais)
```

## Checklist antes de cada push público

- [ ] `git status` sem `.env`, `*.db`, CSV, backups
- [ ] `config.py` só com dados fictícios
- [ ] Nenhuma credencial em código ou docs
- [ ] README e screenshots sem informação pessoal
