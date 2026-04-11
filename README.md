# おはよう (Ohayo)

URL request scheduler with dark/light mode UI.

## Install & Run

```bash
pip install -r requirements.txt
python3 app.py
```

## Build

**macOS:**
```bash
./build_macos.sh
```

**Windows:**
```bash
build_windows.bat
```

## Features

- 🌍 Schedule URL requests
- ⏱️ Custom intervals & stop time
- 📊 Real-time logging
- 🌙 Dark/Light mode
- 🚀 Standalone executables

## Usage

1. Enter URL to request
2. Set interval (seconds)
3. Set stop time (HH:MM)
4. Click Start
5. View logs

## GitHub

```bash
./init_github.sh
git remote add origin https://github.com/YOUR-USERNAME/Ohayo.git
git push -u origin main
```

## GitHub Release Workflow

This project includes a GitHub Actions workflow that:
- automatically creates a new release with a version tag in `0.0.1` format
- detects the previous release tag and increments the version
- releases only macOS and Windows packages
- keeps minor/patch digits between `0` and `9`

Use the workflow on GitHub: `.github/workflows/release.yml`
