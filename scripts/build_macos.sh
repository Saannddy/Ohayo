#!/bin/bash
cd "$(dirname "$0")/.."
rm -rf build/ dist/ *.spec
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --onedir --windowed --name "おはよう" --icon=images/icon.png app.py
echo "✅ macOS app created: dist/おはよう.app"
