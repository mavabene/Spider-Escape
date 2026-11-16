#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GAME="$ROOT/Original_Game_Files"
WORK="$ROOT/build_work"
VENV="$ROOT/.venv"

echo
echo "=========================================="
echo " Spanish Racing — Apple Silicon Mac build"
echo "=========================================="
echo

if [[ "$(uname -m)" != "arm64" ]]; then
  echo "WARNING: This Mac does not report arm64 architecture."
  echo "This kit is intended for Apple Silicon Macs."
  echo
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3 for macOS, then run this script again."
  echo "https://www.python.org/downloads/macos/"
  read -r -p "Press Return to close..."
  exit 1
fi

if [[ ! -f "$GAME/p6.py" ]]; then
  echo "Could not find Original_Game_Files/p6.py."
  read -r -p "Press Return to close..."
  exit 1
fi

echo "1/5  Creating the build environment..."
python3 -m venv "$VENV"

echo "2/5  Installing Pygame and PyInstaller..."
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install pygame pyinstaller

echo "3/5  Preparing a packaging copy of the original game..."
rm -rf "$WORK"
mkdir -p "$WORK/src"

# Copy all original game assets except the alternate easy-mode program.
cp "$GAME/p6.py" "$WORK/src/p6.py"
find "$GAME" -maxdepth 1 -type f ! -name 'p6.py' -exec cp {} "$WORK/src/" \;

# The original code requests background.jpg, while the supplied file is named background.JPG.
# Keep the original untouched and normalize the copied filename for the app bundle.
if [[ -f "$WORK/src/background.JPG" && ! -f "$WORK/src/background.jpg" ]]; then
  cp "$WORK/src/background.JPG" "$WORK/src/background.jpg"
fi

# Add only a resource-directory startup adjustment to the packaging copy.
# This lets the original relative asset filenames resolve inside the frozen .app.
"$VENV/bin/python" - "$WORK/src/p6.py" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
needle = "import sys\n"
shim = (
    "import sys\n"
    "import os\n"
    "if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):\n"
    "    os.chdir(sys._MEIPASS)\n"
)
if "os.chdir(sys._MEIPASS)" not in s:
    if needle not in s:
        raise SystemExit("Could not safely locate the import section in p6.py.")
    s = s.replace(needle, shim, 1)
p.write_text(s)
PY

echo "4/5  Building Spanish Racing.app..."
cd "$WORK/src"
"$VENV/bin/pyinstaller" \
  --noconfirm \
  --clean \
  --windowed \
  --name "Spanish Racing" \
  --osx-bundle-identifier "com.private.spanishracing" \
  --add-data "Jungle.mp3:." \
  --add-data "Tree1sm.png:." \
  --add-data "spider.png:." \
  --add-data "dashboard.png:." \
  --add-data "Jeep.png:." \
  --add-data "spider_mirror.png:." \
  --add-data "right_arrow.png:." \
  --add-data "splat.png:." \
  --add-data "steering-wheel.png:." \
  --add-data "Grindcore Records.otf:." \
  --add-data "Scary Font.ttf:." \
  --add-data "background.jpg:." \
  --add-data "sound.mp3:." \
  --add-data "digital-7.ttf:." \
  p6.py

echo "5/5  Creating a friend-ready ZIP..."
cd "$WORK"
rm -f "$ROOT/Spanish Racing-Mac.zip"
ditto -c -k --sequesterRsrc --keepParent "dist/Spanish Racing.app" "$ROOT/Spanish Racing-Mac.zip"

echo
echo "BUILD COMPLETE"
echo "App: $WORK/src/dist/Spanish Racing.app"
echo "Shareable ZIP: $ROOT/Spanish Racing-Mac.zip"
echo
echo "Please launch the app once on this Mac and play-test it before sending it to friends."
read -r -p "Press Return to close..."
