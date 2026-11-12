"""Точка входа приложения. Поддерживает запуск как модулем, так и напрямую."""

import sys
from pathlib import Path


SRC_DIRECTORY = Path(__file__).resolve().parents[1]
src_path = str(SRC_DIRECTORY)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from tourism.database import initialize_database
from tourism.ui.console import run


def main():
    initialize_database()
    run()


if __name__ == "__main__":
    main()
