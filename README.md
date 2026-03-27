# MD Viewer

A lightweight Markdown viewer and editor that opens `.md` files in your browser. No installation, no dependencies beyond Python 3.

## Features

- **Rendered view** with GitHub-style formatting
- **Syntax-highlighted editor** (CodeMirror with GFM mode)
- **Split mode** with live preview as you type
- **Save to file** via Save button or Ctrl+S
- **Mermaid diagrams** rendered from code blocks
- **Code syntax highlighting** via highlight.js
- **Unsaved changes warning** before closing

## Setup

### Windows

1. Right-click any `.md` file
2. **Open with** > **Choose another app** > **Choose an app on your PC**
3. Browse to `MD Viewer.bat`
4. Check **"Always use this app"**

### Linux

```bash
chmod +x md-viewer.sh
```

Then set `md-viewer.sh` as the default application for `.md` files in your file manager, or via:

```bash
# Create a .desktop file
cat > ~/.local/share/applications/md-viewer.desktop << 'EOF'
[Desktop Entry]
Name=MD Viewer
Exec=/full/path/to/md-viewer.sh %f
Type=Application
MimeType=text/markdown;text/x-markdown;
EOF

# Set as default
xdg-mime default md-viewer.desktop text/markdown
xdg-mime default md-viewer.desktop text/x-markdown
```

### Manual usage

```bash
python3 md_viewer.py path/to/file.md
```

## Mermaid Diagram Examples

### Flowchart

```mermaid
graph TD
    A[Open .md file] --> B{Python installed?}
    B -->|Yes| C[Start local server]
    B -->|No| D[Install Python 3]
    D --> C
    C --> E[Open in browser]
    E --> F{Edit or View?}
    F -->|View| G[Rendered markdown]
    F -->|Edit| H[CodeMirror editor]
    F -->|Split| I[Side-by-side]
    H --> J[Save with Ctrl+S]
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Script as md_viewer.py
    participant Server as HTTP Server
    participant Browser

    User->>Script: Double-click .md file
    Script->>Server: Start on random port
    Script->>Browser: Open localhost URL
    Browser->>Server: GET /
    Server->>Browser: HTML + markdown content
    User->>Browser: Click Edit
    User->>Browser: Make changes
    User->>Browser: Ctrl+S
    Browser->>Server: POST /save
    Server->>Script: Write to .md file
    Server->>Browser: OK
```

### Class Diagram

```mermaid
classDiagram
    class Handler {
        +do_GET()
        +do_POST()
        -_serve_page()
        -_serve_content()
        -_handle_save()
    }
    class HTTPServer {
        +serve_forever()
        +server_close()
    }
    Handler --|> BaseHTTPRequestHandler
    HTTPServer --> Handler : uses
```

### State Diagram

```mermaid
stateDiagram-v2
    [*] --> View : Open file
    View --> Edit : Click Edit
    View --> Split : Click Split
    Edit --> View : Click View
    Edit --> Split : Click Split
    Split --> View : Click View
    Split --> Edit : Click Edit
    Edit --> Edit : Ctrl+S (save)
    Split --> Split : Ctrl+S (save)
```

## Requirements

- Python 3.6+
- A web browser
- Internet connection (for CDN libraries on first load; browsers cache them after that)
