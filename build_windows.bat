@echo off
rmdir /s /q build dist 2>nul
del /q *.spec 2>nul
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist icon.ico (
    python -c "from PIL import Image; img = Image.open('images/icon.png'); img.save('icon.ico', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
)
pyinstaller --onefile --windowed --name "Ohayo" --icon=icon.ico app.py
echo ✅ Windows app created: dist\Ohayo.exe
