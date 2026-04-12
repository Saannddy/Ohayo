# おはよう (Ohayo)

> **"Good Morning"** — A beautiful, modern URL request scheduler with Japanese sunrise theme and real-time stats.

## ✨ Features

- 🌅 **Beautiful Modern UI** — Dark/Light mode with smooth transitions
- 📊 **Real-time Stats** — Track total requests, success rate, avg response time
- ⏱️ **Smart Scheduling** — Custom intervals + stop time (HH:MM)
- 🔄 **HTTP Methods** — GET, POST, PUT, PATCH, DELETE, HEAD
- 📋 **Custom Headers** — Key/value editor for each request
- 📝 **Request Body** — Raw body support for POST/PUT
- 🔍 **Live Filtering** — Filter logs by 2xx/3xx/4xx/5xx/ERR
- ⬇️ **Export Logs** — Save logs as .txt or .csv
- 💾 **Profile Management** — Save and load URL + config presets
- ⏳ **Visual Feedback** — Countdown bar + animated status indicator
- 🎨 **Emoji-rich UI** — Clean, intuitive icons throughout

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```

## 📦 Build & Distribution

### macOS
```bash
./scripts/build_macos.sh
# Creates: dist/おはよう.app
# Run: open dist/おはよう.app
```

### Windows
```bash
scripts\build_windows.bat
# Creates: dist\Ohayo.exe
# Run: dist\Ohayo.exe
```

## 🎨 UI/UX Improvements

### Recent Updates (v2.0)
- ✅ **Fixed macOS build issues** — Assets now properly bundled
- ✅ **Redesigned UI** — Modern layout with sidebar + main panel
- ✅ **Better dark/light mode** — Smooth theme transitions
- ✅ **Enhanced styling** — Better spacing, typography, colors
- ✅ **Improved accessibility** — Larger touch targets, clearer labels
- ✅ **Emoji integration** — Visual indicators throughout the app
- ✅ **Responsive layout** — Works on different screen sizes

## 🏗️ Project Structure

```
Ohayo/
├── app.py                    # Entry point
├── src/
│   ├── ui/
│   │   ├── modern_ui.py     # Beautiful new UI (primary)
│   │   ├── main_window.py   # Original UI (fallback)
│   │   ├── widgets.py       # Custom widgets
│   │   └── __init__.py
│   ├── theme/
│   │   ├── themes.py        # Dark/Light theme definitions
│   │   └── __init__.py
│   ├── core/
│   │   ├── scheduler.py     # Request scheduling engine
│   │   ├── profiles.py      # Profile save/load
│   │   └── __init__.py
│   └── __init__.py
├── scripts/
│   ├── build_macos.sh       # macOS build script
│   └── build_windows.bat    # Windows build script
├── images/
│   └── icon.png             # App icon
├── requirements.txt         # Python dependencies
└── README.md
```

## 🔧 Requirements

- Python 3.8+
- tkinter (usually included with Python)
- Pillow (for image handling)
- requests (for HTTP requests)

See `requirements.txt` for full dependencies.

## 🐛 Troubleshooting

**App won't open on macOS:**
- Try: `open dist/おはよう.app`
- Check permissions: `xattr -d com.apple.quarantine "dist/おはよう.app"`

**macOS security warning:**
- App is unsigned (sign with your own certificate for distribution)
- Or allow from System Preferences > Security & Privacy

**Missing images:**
- Rebuild the app: `./scripts/build_macos.sh`

## 📝 Development

### Adding new themes
Edit `src/theme/themes.py` to customize colors.

### Creating custom widgets
Add to `src/ui/widgets.py` and import in `modern_ui.py`.

### Building for distribution
macOS signing/notarization requires developer certificates. See `.github/workflows/release.yml` for CI/CD setup.

## 📄 License

MIT License - See LICENSE for details.

## 🎉 Credits

Built with Python, Tkinter, and ☕ coffee.

---

**Enjoy scheduling!** 🚀

Ohayo/
├── app.py                  # Entry point
├── requirements.txt
├── images/icon.png
├── scripts/
│   ├── build_macos.sh
│   └── build_windows.bat
└── src/
    ├── theme/
    │   └── themes.py       # Asahi dark/light color tokens + fonts
    ├── core/
    │   ├── scheduler.py    # HTTP scheduler (threading + callbacks)
    │   └── profiles.py     # Profile save/load (~/.ohayo_profiles.json)
    └── ui/
        ├── widgets.py      # Custom widgets: gradient header, dot, bar, cards
        └── main_window.py  # Full two-panel UI
```

## Usage

1. Select HTTP **Method** (GET, POST, PUT…)
2. Enter **URL** to request
3. Set **Interval** in seconds between requests
4. Set **Stop Time** in HH:MM (24-hour)
5. Optionally add **Headers** and **Body**
6. Click **▶ START**
7. Watch live stats and log entries stream in
8. Use filter pills to view only 2xx / errors / etc.
9. **Export** the log when done

## Build

**macOS:**

```bash
./scripts/build_macos.sh
```

**Windows:**

```bash
scripts/build_windows.bat
```

## Profiles

Profiles are stored in `~/.ohayo_profiles.json`.  
Use **💾 Save**, **📂 Load**, and **🗑 Delete** in the sidebar.
