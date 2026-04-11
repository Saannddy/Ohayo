#!/bin/bash
rm -rf build/ dist/ *.spec
pyinstaller --onefile --windowed --name "おはよう" --icon=icon.png app.py
echo "✅ macOS app created: dist/おはよう.app"
