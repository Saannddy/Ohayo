# おはよう — API Waker

> **"Good Morning"** — A native desktop HTTP request scheduler with a deep-space Japanese sunrise theme, real-time stats, and a beautiful glassmorphism UI.

Built with **Tauri 2** (Rust backend) + **React / TypeScript** frontend.

---

## Features

- **3 scheduling modes** — Once, Repeat N times, Continuous until HH:MM
- **All HTTP methods** — GET POST PUT PATCH DELETE HEAD OPTIONS
- **Custom headers** — Key/value editor per request
- **Request body** — Raw body for POST / PUT / PATCH
- **Live response log** — Color-coded by status (2xx / 3xx / 4xx / 5xx / ERR)
- **Real-time stats** — Total, success %, avg ms, last status code
- **Collections** — Save and reload request presets (stored in `~/.ohayo_profiles.json`)
- **Export log** — Download as `.txt`
- **Dark / Light theme** — Toggle in the sidebar
- **Animated starfield** — 220-star canvas background

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 18 + | [nodejs.org](https://nodejs.org) |
| Rust + Cargo | stable | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| npm | 9 + | bundled with Node |

> **macOS only:** Xcode Command Line Tools are required.
> ```bash
> xcode-select --install
> ```

After installing Rust, reload your shell (or open a new terminal):
```bash
source "$HOME/.cargo/env"
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-username/Ohayo.git
cd Ohayo

# 2. Install JS dependencies
npm install

# 3. Run in development mode
npm run tauri dev
```

> **First run takes 5–10 minutes** — Rust compiles ~400 crates and caches them.
> Every subsequent run starts in under 10 seconds.

---

## Build (production binary)

```bash
npm run tauri build
```

Output: `src-tauri/target/release/bundle/`
- macOS → `.dmg` + `.app`
- Windows → `.msi` + `.exe`
- Linux → `.deb` + `.AppImage`

---

## Docker (web preview only)

The Docker setup runs the **Vite frontend** in a browser.
Tauri-native features (file system, profiles) are not available in Docker.

```bash
# Development (hot-reload at http://localhost:1420)
docker compose up

# Production web build
docker build --target prod -t ohayo-web .
docker run -p 80:80 ohayo-web
```

---

## Project Structure

```
Ohayo/
├── src/                        # React / TypeScript frontend
│   ├── App.tsx
│   ├── components/
│   │   ├── StarField.tsx       # Canvas starfield animation
│   │   ├── Sidebar.tsx         # Collections + theme toggle
│   │   ├── RequestBar.tsx      # Method / URL / Send button
│   │   ├── Tabs.tsx            # Send Mode | Headers | Body
│   │   ├── tabs/
│   │   │   ├── SendModeTab.tsx
│   │   │   ├── HeadersTab.tsx
│   │   │   └── BodyTab.tsx
│   │   ├── LogPanel.tsx        # Response log container
│   │   ├── LogEntries.tsx      # Log list + filter pills
│   │   ├── LogHeader.tsx       # Title + export + clear
│   │   └── StatsRow.tsx        # 4-chip stats row
│   ├── hooks/
│   │   ├── useScheduler.ts     # Tauri event listeners + invoke
│   │   ├── useProfiles.ts      # Profile CRUD
│   │   └── useTheme.ts         # Dark/light toggle
│   └── store/
│       └── appStore.ts         # Zustand global state
│
├── src-tauri/                  # Rust backend
│   ├── src/
│   │   ├── main.rs
│   │   ├── lib.rs              # Tauri commands
│   │   ├── scheduler.rs        # Async HTTP loop (tokio + reqwest)
│   │   ├── profiles.rs         # ~/.ohayo_profiles.json
│   │   ├── http_client.rs      # HTTP execution
│   │   └── types.rs            # Shared types
│   └── tauri.conf.json
│
├── Dockerfile                  # Web-only preview
├── docker-compose.yml
└── package.json
```

---

## Troubleshooting

**`cargo: command not found` or `failed to run cargo metadata`**
```bash
source "$HOME/.cargo/env"
# Then add to your shell profile permanently:
echo '. "$HOME/.cargo/env"' >> ~/.zshrc   # zsh
echo '. "$HOME/.cargo/env"' >> ~/.bashrc  # bash
```

**Window doesn't appear after `npm run tauri dev`**
First-time Rust compilation takes 5–10 minutes. Wait for:
```
Running app...
```
to appear in the terminal — the window opens right after.

**macOS security warning on built app**
```bash
xattr -d com.apple.quarantine "src-tauri/target/release/bundle/macos/Ohayo.app"
```

**Profiles not loading**
Profiles are stored in `~/.ohayo_profiles.json`. The file is created automatically on first save.

---

## License

MIT
