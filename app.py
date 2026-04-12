import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui import run_app

if __name__ == "__main__":
    run_app()
