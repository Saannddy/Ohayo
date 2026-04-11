@echo off
rmdir /s /q build dist 2>nul
del /q *.spec 2>nul
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --onefile --windowed --name "Ohayo" --icon=icon.ico app.py
echo ✅ Windows app created: dist\Ohayo.exe
