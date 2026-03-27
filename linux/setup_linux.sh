#!/bin/bash
# Register MD Viewer as default .md handler with icon (no root required)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ICON="$SCRIPT_DIR/md-viewer.png"
LAUNCHER="$SCRIPT_DIR/md-viewer.sh"

# Ensure launcher is executable
chmod +x "$LAUNCHER"

# Install icon for the custom app
xdg-icon-resource install --novendor --size 256 "$ICON" md-viewer

# Create .desktop file
DESKTOP_FILE="$HOME/.local/share/applications/md-viewer.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=MD Viewer
Comment=Lightweight Markdown viewer and editor
Exec=$LAUNCHER %f
Icon=md-viewer
Type=Application
Categories=Utility;TextEditor;
MimeType=text/markdown;text/x-markdown;
EOF

# Register MIME types
xdg-mime default md-viewer.desktop text/markdown
xdg-mime default md-viewer.desktop text/x-markdown

# Update desktop database
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null

echo ""
echo "Done! MD Viewer is now the default app for .md files."
echo "You may need to log out/in for the icon to appear everywhere."
