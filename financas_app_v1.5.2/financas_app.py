"""Compatibilidade com versões antigas.

Você ainda pode rodar:
    python financas_app.py

Internamente, o app agora usa a estrutura modular em main.py, db.py, utils.py e ui/.
"""

from main import main


if __name__ == "__main__":
    main()
