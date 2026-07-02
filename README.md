# get-your-stuff-together
finaz programm

## Installation

Fertige Binaries werden automatisch über eine GitHub Action gebaut (siehe
[`.github/workflows/build.yml`](.github/workflows/build.yml)). Der Workflow
heißt `Build Executables` und macht Folgendes:

- **Trigger:** läuft automatisch, wenn ein Tag im Format `v*` gepusht wird
  (z. B. `v1.0`), oder manuell über `workflow_dispatch` (Button "Run workflow"
  in der GitHub-UI bzw. per `gh` CLI).
- **Zwei parallele Jobs:**
  - `build-linux` auf `ubuntu-latest`
  - `build-windows` auf `windows-latest`
- Beide Jobs machen dasselbe: Python 3.12 aufsetzen, Abhängigkeiten
  (`pyinstaller pandas tabulate rich prompt-toolkit`) installieren, dann
  `pyinstaller financ-app.spec` im Ordner `CLI_finaz` ausführen.
- Am Ende lädt jeder Job das fertige Binary als **Artifact** hoch:
  - Linux → Artifact `financ-app-linux` (enthält `financ-app`)
  - Windows → Artifact `financ-app-windows` (enthält `financ-app.exe`)

Artifacts sind nur auf der GitHub-Weboberfläche (Tab "Actions") download­bar
und laufen standardmäßig nach 90 Tagen ab – es gibt (noch) keinen
GitHub-Release-Schritt.

### 1. Build auslösen

```bash
# per Tag (löst den Workflow automatisch aus)
git tag v1.0
git push --tags

# oder manuell ohne Tag (benötigt GitHub CLI, gh auth login vorher einmalig)
gh workflow run build.yml
```

### 2. Fertiges Binary herunterladen

```bash
# letzten Workflow-Run finden
gh run list --workflow=build.yml --limit 1

# Artifact für Linux herunterladen (lädt einen Ordner mit "financ-app" ins aktuelle Verzeichnis)
gh run download <RUN_ID> -n financ-app-linux

# Artifact für Windows herunterladen (lädt einen Ordner mit "financ-app.exe")
gh run download <RUN_ID> -n financ-app-windows
```

Alternativ: im Browser zu **Actions → Build Executables → gewünschter Run**
navigieren und die Artifacts unten auf der Seite herunterladen.

### 3a. Installation unter Linux

```bash
# ausführbar machen
chmod +x financ-app

# ins PATH legen, damit "financ-app" von überall startbar ist
sudo cp financ-app /usr/local/bin/

# starten
financ-app
```

### 3b. Installation unter Windows

```powershell
# im heruntergeladenen Ordner direkt starten
.\financ-app.exe

# optional: in einen Ordner legen, der im PATH ist, damit es global aufrufbar ist
# (z.B. C:\Tools\financ-app\), danach diesen Ordner einmalig zu PATH hinzufügen
```

### Alternative: lokal selbst bauen (ohne GitHub Action)

Falls kein GitHub-Zugriff nötig sein soll, gibt es in `CLI_finaz/` passende
Build-Skripte, die denselben `financ-app.spec` verwenden:

```bash
# Linux
cd CLI_finaz
./build_linux.sh
# Ergebnis: dist/financ-app
```

```powershell
# Windows
cd CLI_finaz
build_windows.bat
# Ergebnis: dist\financ-app.exe
```

Beide Skripte installieren `pyinstaller` bei Bedarf automatisch nach und
räumen alte `build/`- und `dist/`-Ordner vorher auf.

### Alternative: aus dem Quellcode direkt starten (ohne Build)

```bash
cd CLI_finaz
source .venv/bin/activate.fish
# oder: eval (poetry env activate)

python scr/main.py
```