import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ui.main_window import run_app

if __name__ == "__main__":
    run_app()
