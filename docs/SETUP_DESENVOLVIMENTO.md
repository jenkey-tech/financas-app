# Setup de desenvolvimento — Finanças App

Guia para configurar ambiente local na base **v3.4.3**.

---

## Pré-requisitos

| Requisito | Versão mínima sugerida |
|-----------|------------------------|
| Python | 3.10+ |
| pip | recente |
| Git | qualquer (opcional) |
| SO | Windows (desenvolvido/testado), Linux/macOS compatível |

Tkinter geralmente vem com Python no Windows. No Linux:

```bash
# Debian/Ubuntu
sudo apt install python3-tk
```

---

## 1. Clonar o repositório

```bash
git clone https://github.com/jenkey-tech/financas-app.git
cd financas-app
```

---

## 2. Ambiente virtual (recomendado)

### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Cloud (opcional):
pip install -r requirements-cloud.txt
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Cloud (opcional):
pip install -r requirements-cloud.txt
```

---

## 3. Executar o app

```bash
python main.py
```

Alternativa compatível:

```bash
python financas_app.py
```

Na primeira execução:

- Cria `financas.db` automaticamente
- Insere categorias padrão e dados históricos se o banco estiver vazio
- Cria pastas `backups/` e `exports/` quando necessário

---

## 4. Configuração Supabase (opcional)

### 4.1 Criar projeto

1. Acesse [supabase.com](https://supabase.com) e crie um projeto
2. No **SQL Editor**, execute o conteúdo de `sql/supabase_schema.sql`

### 4.2 Configurar variáveis

```powershell
copy .env.example .env
```

Edite `.env`:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_chave_anon_public
```

> **Segurança:** nunca commite `.env`. O arquivo está no `.gitignore`.

### 4.3 Validar no app

1. Abra o app — deve exibir `Supabase Cloud + cache rápido` no título
2. Clique **Validar banco de dados**
3. Use **Sincronizar base** para enviar dados locais
4. Use **Recarregar dados** para sync bidirecional

Sem `.env`, o app funciona apenas com SQLite local.

---

## 5. Estrutura de arquivos gerados

| Arquivo/Pasta | Versionado | Descrição |
|---------------|------------|-----------|
| `financas.db` | Não | Banco SQLite local |
| `.env` | Não | Credenciais Supabase |
| `backups/` | Não | Backups automáticos |
| `exports/` | Não | CSVs exportados |
| `venv/` | Não | Ambiente virtual |

---

## 6. Dependências

```text
matplotlib==3.10.3
ttkbootstrap==1.14.2
supabase==2.15.3   # requirements-cloud.txt
```
```

- **matplotlib** — gráficos nas abas Dashboard e Insights
- **supabase** — sync cloud (só necessário com `.env`)
- **ttkbootstrap** — tema visual; app abre sem ele usando tema padrão

---

## 7. Fluxo de desenvolvimento

### Editar código

1. Faça alterações nos módulos (`db.py`, `ui/app.py`, etc.)
2. Reinicie o app para testar (`python main.py`)
3. Não há hot-reload

### Testar sync

1. Configure `.env` com projeto Supabase de teste
2. Teste offline (renomeie `.env` temporariamente)
3. Teste sync entre duas máquinas com mesmo `.env`

### Versionar dados (opcional)

O botão **Commit estado atual** no app:

1. Copia `financas.db` → `backups/estado_anterior.db`
2. Exporta CSV para `exports/`
3. Executa `git add .` + `git commit`

Push para GitHub permanece manual:

```bash
git push
```

---

## 8. Solução de problemas

### App não abre / erro Tkinter

- Instale `python3-tk` (Linux) ou reinstale Python com Tcl/Tk (Windows)

### `no such column: updated_at`

- Abra o app normalmente — `init_db()` migra schema automaticamente
- Ou delete `financas.db` para recriar (perde dados locais)

### Sync falha

- Verifique `SUPABASE_URL` e `SUPABASE_KEY`
- Confirme que `sql/supabase_schema.sql` foi executado no Supabase
- Use **Validar banco de dados** para diagnóstico

### Gráficos não aparecem

```bash
pip install matplotlib
```

### Git não encontrado (Commit estado atual)

- Instale [Git for Windows](https://git-scm.com/) e reinicie o terminal

---

## 9. Documentação complementar

| Documento | Conteúdo |
|-----------|------------|
| [AI_CONTEXT.md](./AI_CONTEXT.md) | Contexto para IA e onboarding rápido |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Arquitetura detalhada |
| [DECISIONS.md](./DECISIONS.md) | Decisões técnicas |
| [ROADMAP.md](./ROADMAP.md) | Evolução planejada |
| [CHANGELOG.md](./CHANGELOG.md) | Histórico de versões |

---

## 10. Checklist de PR

- [ ] App abre sem erros (`python main.py`)
- [ ] Modo offline funciona sem `.env`
- [ ] Nenhum secret commitado (`.env`, tokens)
- [ ] `APP_VERSION` atualizado se release
- [ ] Entrada no `CHANGELOG.md` se mudança visível
- [ ] Decisão registrada em `DECISIONS.md` se arquitetural
