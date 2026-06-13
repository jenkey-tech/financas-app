"""Ponto de entrada do app de finanças."""

from db import init_db
from ui.app import App


def main():
    init_db()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
