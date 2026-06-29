#!/usr/bin/env bash
set -e

echo "=== financ-app Linux Build ==="

# PyInstaller installieren falls nicht vorhanden
if ! command -v pyinstaller &>/dev/null; then
    pip install pyinstaller
fi

# Altes Build aufräumen
rm -rf build/ dist/

# Binary bauen
pyinstaller financ-app.spec

echo ""
echo "Fertig! Binary liegt unter: dist/financ-app"
echo "Verschiebe es irgendwo in deinen PATH, z.B.:"
echo "  sudo cp dist/financ-app /usr/local/bin/"
