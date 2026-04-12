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
./scripts/build_macos.sh
```

**Windows:**
```bash
scripts/build_windows.bat
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

## GitHub Release Workflow

The workflow builds and publishes both:
- macOS ZIP release (`Ohayo-macos.zip`)
- Windows ZIP release (`Ohayo-windows.zip`)

Secrets to enable signing and notarization:
- `MACOS_CERTIFICATE` (base64 `.p12`)
- `MACOS_CERT_PASSWORD`
- `MACOS_SIGNING_IDENTITY`
- `MACOS_KEYCHAIN_PASSWORD`
- `APPLE_ID`
- `APPLE_APP_SPECIFIC_PASSWORD`
- `APPLE_TEAM_ID`
- `WINDOWS_CERTIFICATE` (base64 `.pfx`)
- `WINDOWS_CERT_PASSWORD`

If signing secrets are present, the workflow will sign and notarize the macOS app and sign the Windows executable before release.
