@echo off
rmdir /s /q build dist 2>nul
del *.spec 2>nul
pyinstaller --onefile --windowed --name "Ohayo" --icon=icon.ico app.py
echo ✅ Windows app created: dist\Ohayo.exe
