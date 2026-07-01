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
- **Response inspector** — Dedicated Logs page with full response body (pretty JSON) + headers
- **Real-time stats** — Total, success %, avg ms, last status code
- **Collections** — Bruno-style folders of `.ohy` request files in a folder you pick on disk
- **Import / Export** — Bundle a whole collection to a single `.ohy` file and back
- **Environment variables** — Per-collection environments; reference as `{{name}}` in URL, headers, body
- **Delete confirmation** — Modal shows exactly what will be removed
- **Dark / Light theme** — Toggle in the sidebar
- **Animated starfield** — Canvas background

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

> **Linux only:** Tauri needs system libraries (WebKitGTK, GTK, etc.) that are **not** installed by `npm install` or `cargo`. Install them from your distro before building.
>
> **Arch / Manjaro**
> ```bash
> sudo pacman -S --needed \
>   webkit2gtk-4.1 base-devel curl wget file openssl \
>   appmenu-gtk-module libappindicator-gtk3 librsvg
> ```
>
> **Debian / Ubuntu**
> ```bash
> sudo apt update && sudo apt install -y \
>   libwebkit2gtk-4.1-dev build-essential curl wget file \
>   libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
> ```
>
> **Fedora**
> ```bash
> sudo dnf install -y webkit2gtk4.1-devel openssl-devel curl wget file \
>   libappindicator-gtk3-devel librsvg2-devel && sudo dnf group install -y "C Development Tools and Libraries"
> ```
>
> See [Tauri prerequisites](https://tauri.app/start/prerequisites/) for other distros.

After installing Rust, reload your shell (or open a new terminal):
```bash
source "$HOME/.cargo/env"
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/Saannddy/Ohayo.git
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

## Collections (`.ohy`)

A collection is just a folder you pick on disk. Each saved request is one
pretty-printed JSON file with the `.ohy` extension; subfolders group requests.
Environments live in an `environments/` subfolder.

```
MyCollection/
├── collection.ohy           # collection metadata
├── environments/
│   ├── dev.ohy              # { "name": "dev", "vars": { "host": "..." } }
│   └── prod.ohy
├── GitHub/
│   └── list-repos.ohy
└── health-check.ohy
```

Because it's plain files in a folder, collections are git-friendly and portable.
Use **Export** to bundle the whole tree into a single `.ohy` file, and **Import**
to reconstruct it elsewhere.

---

## Project Structure

```
Ohayo/
├── src/                        # React / TypeScript frontend
│   ├── App.tsx
│   ├── components/
│   │   ├── StarField.tsx       # Canvas starfield animation
│   │   ├── TopNav.tsx          # Page tabs + env selector + Save Current
│   │   ├── Sidebar.tsx         # Collection tree + import/export + theme
│   │   ├── CollectionTree.tsx  # Recursive folder/request tree
│   │   ├── Modal.tsx           # Portal dialog (delete confirm, save, etc.)
│   │   ├── EnvSelector.tsx     # Active environment dropdown
│   │   ├── EnvironmentsPage.tsx# Manage environments + variables
│   │   ├── LogsPage.tsx        # Response inspector (body + headers)
│   │   ├── RequestBar.tsx      # Method / URL / Send button
│   │   ├── Tabs.tsx            # Send Mode | Headers | Body
│   │   ├── tabs/{SendModeTab,HeadersTab,BodyTab}.tsx
│   │   ├── LogPanel.tsx        # Burning-rope progress + compact log
│   │   ├── LogEntries.tsx, LogHeader.tsx, StatsRow.tsx
│   ├── hooks/
│   │   ├── useScheduler.ts     # Tauri event listeners + invoke
│   │   ├── useCollections.ts   # Collection / request / env CRUD
│   │   └── useTheme.ts         # Dark/light toggle
│   ├── lib/
│   │   └── vars.ts             # {{name}} variable resolution
│   └── store/
│       └── appStore.ts         # Zustand global state
│
├── src-tauri/                  # Rust backend
│   ├── src/
│   │   ├── main.rs, lib.rs     # Tauri commands
│   │   ├── scheduler.rs        # Async HTTP loop (tokio + reqwest)
│   │   ├── collections.rs      # `.ohy` folder/file store
│   │   ├── config.rs           # Last-opened collection
│   │   ├── http_client.rs      # HTTP execution (+ response body)
│   │   └── types.rs            # Shared types
│   └── tauri.conf.json
│
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

**Linux build fails: `webkit2gtk` / `glib` / `gdk` not found (missing dependencies)**
System libraries are missing. `npm install` and `cargo` do **not** provide these — install them from your distro. See the **Linux only** note under [Prerequisites](#prerequisites). On Arch:
```bash
sudo pacman -S --needed webkit2gtk-4.1 base-devel curl wget file openssl \
  appmenu-gtk-module libappindicator-gtk3 librsvg
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

**Collection not reopening**
The last-opened collection path is remembered in `<config-dir>/ohayo/config.json`
(e.g. `~/Library/Application Support/ohayo/config.json` on macOS). If the folder was
moved or deleted, just open it again from the sidebar.

---

## License

MIT
