# Finanças App

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Database](https://img.shields.io/badge/Database-SQLite-blue)
![Cloud](https://img.shields.io/badge/Cloud-Supabase-success)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-3.4.3-orange)

A modern **personal finance desktop application** built with Python, featuring an intuitive graphical interface, expense tracking, dashboards, financial insights, cash flow analysis, and financial goal management.

The application follows an **offline-first architecture**, storing all data locally using SQLite while offering optional cloud synchronization through Supabase.

---

# Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Cloud Synchronization](#cloud-synchronization)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Security](#security)
- [Development Philosophy](#development-philosophy)
- [Roadmap](#roadmap)
- [License](#license)

---

# Features

- 📊 Interactive financial dashboard
- 💳 Expense management by category
- 📅 Upcoming payments and due date tracking
- 🔄 Automatic payment status
- 📈 Cash flow analysis
- 🎯 Financial goals
- 💡 Spending insights and trends
- ☁️ Optional cloud synchronization
- 📴 Offline-first operation
- 🧪 Demo dataset for testing

---

# Screenshots

> *Screenshots will be added soon.*

You can replace this section with images such as:

```markdown
![Dashboard](docs/images/dashboard.png)

![Cash Flow](docs/images/cashflow.png)

![Goals](docs/images/goals.png)
```

---

# Technology Stack

| Layer | Technology |
|--------|------------|
| Language | Python 3.10+ |
| UI | Tkinter |
| Theme | ttkbootstrap |
| Charts | matplotlib |
| Local Database | SQLite |
| Cloud Sync | Supabase |
| Version Control | Git |
| Documentation | Markdown |

---

# Architecture

```text
                    +----------------------+
                    |   Desktop Interface  |
                    |   (Tkinter UI)       |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Business Logic Layer |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | SQLite Local Storage |
                    +----------+-----------+
                               |
                               |
                    Async Sync Queue
                               |
                               v
                    +----------------------+
                    |    Supabase Cloud    |
                    |    (Optional Sync)   |
                    +----------------------+
```

## Design Principles

- Offline-first
- Modular architecture
- Separation of concerns
- Local data ownership
- Optional cloud synchronization
- Secure credential management

---

# Getting Started

## Clone the repository

```bash
git clone https://github.com/jenkey-tech/financas-app.git

cd financas-app
```

---

## Create a virtual environment

### Windows

```powershell
python -m venv venv

.\venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the application

```bash
python main.py
```

During the first execution the application automatically creates the local SQLite database.

No sample data is inserted by default.

To populate demonstration data, manually execute:

```python
seed_demo_data()
```

from `db.py`.

Demo records are marked with `is_demo=1` and are never synchronized with Supabase.

---

# Cloud Synchronization

Cloud synchronization is completely optional.

Install additional dependencies:

```bash
pip install -r requirements-cloud.txt
```

Create your environment file:

```bash
copy .env.example .env
```

Configure your Supabase project:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

Run the database schema:

```
sql/supabase_schema.sql
```

Inside the application:

```
Validate Database
↓

Reload Data
```

---

# Project Structure

```text
financas-app/
│
├── main.py
├── financas_app.py
├── config.py
├── db.py
├── utils.py
│
├── ui/
│   └── app.py
│
├── sql/
│   └── supabase_schema.sql
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   ├── ROADMAP.md
│   ├── SETUP_DESENVOLVIMENTO.md
│   └── REPOSITORIOS.md
│
├── requirements.txt
├── requirements-cloud.txt
├── CHANGELOG.md
└── LICENSE
```

---

# Documentation

| Document | Description |
|----------|-------------|
| **ARCHITECTURE.md** | Overall architecture and data flow |
| **DECISIONS.md** | Architectural Decision Records (ADR) |
| **ROADMAP.md** | Planned features |
| **SETUP_DESENVOLVIMENTO.md** | Development environment |
| **CHANGELOG.md** | Version history |
| **REPOSITORIOS.md** | Public vs private repository strategy |

---

# Security

The following files are intentionally excluded from version control:

- `.env`
- SQLite databases
- User backups
- CSV exports
- Excel exports

Sensitive credentials and personal financial information are never committed.

For production deployments, enabling **Supabase Authentication** and **Row Level Security (RLS)** is strongly recommended.

---

# Development Philosophy

This repository contains the **public portfolio version** of the project.

The objective is not only to demonstrate application functionality, but also software engineering practices such as:

- Project organization
- Documentation
- Architecture
- Versioning
- Maintainability
- Secure development

---

# Roadmap

Planned future improvements include:

- [ ] Docker support
- [ ] GitHub Actions CI
- [ ] Unit tests
- [ ] Integration tests
- [ ] Authentication
- [ ] Multi-user support
- [ ] REST API
- [ ] Cloud-first deployment
- [ ] Performance improvements
- [ ] Reporting enhancements

---

# Contributing

Suggestions, improvements and bug reports are always welcome.

Feel free to open an Issue or submit a Pull Request.

---

# License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.
