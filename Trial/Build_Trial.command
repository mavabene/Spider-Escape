#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../Spanish_Racing_Mac_Builder" && pwd)"
GAME="$ROOT/../Finalp6"
TRIAL="$ROOT/../Trial"
WORK="$(mktemp -d /tmp/spider-escape-build.XXXXXX)"
VENV="$ROOT/.venv-arm64"
export PYINSTALLER_CONFIG_DIR="$WORK/pyinstaller-cache"

echo
echo "=========================================="
echo " Spider Escape 2.0.3 Trial — Mac build"
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
  true
  exit 1
fi

if [[ ! -f "$GAME/p6.py" ]]; then
  echo "Could not find ../Finalp6/p6.py."
  true
  exit 1
fi

echo "1/5  Preparing the build environment..."
if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
fi

echo "2/5  Checking Pygame and PyInstaller..."
if ! "$VENV/bin/python" -c 'import pygame, PyInstaller' >/dev/null 2>&1; then
  "$VENV/bin/python" -m pip install pygame pyinstaller
fi

echo "3/5  Preparing a packaging copy of the original game..."
mkdir -p "$WORK"
mkdir -p "$WORK/src"

# Copy all original game assets except the alternate easy-mode program.
cp "$TRIAL/game.py" "$WORK/src/p6.py"
cp "$TRIAL/rules.py" "$WORK/src/rules.py"
find "$GAME" -maxdepth 1 -type f ! -name 'p6.py' -exec cp {} "$WORK/src/" \;

echo "4/5  Building Spider Escape 2.0.3 Trial.app..."
cd "$WORK/src"
"$VENV/bin/python" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "Spider Escape 2.0.3 Trial" \
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
  --add-data "background.JPG:." \
  --add-data "sound.mp3:." \
  --add-data "digital-7.ttf:." \
  p6.py

echo "5/5  Verifying the app and packaged ZIP..."
APP="$WORK/src/dist/Spider Escape 2.0.3 Trial.app"
# Keep signing and app bundles outside cloud-synced folders.
xattr -cr "$APP"
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString 2.0.3" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleVersion string 2.0.3" "$APP/Contents/Info.plist"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"
ZIP="$ROOT/Spider Escape-2.0.3-Trial-Mac.zip"
ditto --norsrc --noextattr -c -k --keepParent "$APP" "$ZIP"
mkdir "$WORK/verify"
ditto -x -k "$ZIP" "$WORK/verify"
VERIFIED_APP="$WORK/verify/Spider Escape 2.0.3 Trial.app"
codesign --verify --deep --strict "$VERIFIED_APP"
shasum -a 256 "$ZIP" > "$ZIP.sha256"

LOCAL_APP="$TRIAL/Spider Escape 2.0.3 Trial.app"
PREVIOUS_APP="$WORK/previous.app"
if [[ -e "$LOCAL_APP" ]]; then
  mv "$LOCAL_APP" "$PREVIOUS_APP"
fi
if ! mv "$VERIFIED_APP" "$LOCAL_APP"; then
  if [[ -e "$PREVIOUS_APP" ]]; then
    mv "$PREVIOUS_APP" "$LOCAL_APP"
  fi
  exit 1
fi
echo "BUILD COMPLETE"
echo "Verified app: $LOCAL_APP"
echo "Send this ZIP: $ZIP"
echo "This locally signed app is not Apple-notarized; recipients may need Privacy & Security > Open Anyway."
