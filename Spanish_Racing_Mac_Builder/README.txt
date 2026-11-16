# Spanish Racing — Mac build kit (Apple Silicon)

This kit builds a standalone macOS application from the original regular game (`p6.py`).
It does not use `p6easy.py`, and it does not intentionally change game mechanics, scoring,
difficulty, quiz behavior, graphics, sound, or timing.

## Build it on your Apple Silicon Mac

1. Extract this ZIP.
2. Open the extracted `Spanish_Racing_Mac_Builder` folder.
3. Control-click `Build_Mac.command` and choose **Open**. Confirm Open if macOS asks.
4. The script creates a local Python environment, installs Pygame and PyInstaller, and builds
   `Spanish Racing.app`.
5. When it finishes, find:
   - `dist/Spanish Racing.app`
   - `Spanish Racing-Mac.zip`

The first build requires an internet connection to install the build tools. It can take a few
minutes. You do not need to install Python packages yourself or edit the game.

## What to send your friends

Send `Spanish Racing-Mac.zip`. Your friends should:
1. Extract the ZIP.
2. Move `Spanish Racing.app` to Applications (optional).
3. Control-click the app and choose **Open** the first time if macOS blocks an app from an
   unidentified developer. They may need to confirm Open once more.

This is an unsigned private-distribution build. It is suitable for sharing with a few friends,
but macOS may show a Gatekeeper warning. Apple's Developer ID signing and notarization would
be needed for a smoother public download experience.

## Important compatibility note

This build is for Apple Silicon Macs (M-series). It is not a Windows build and is not guaranteed
to run natively on Intel Macs.

## Faithfulness and packaging note

The original `p6.py` and original artwork/audio/font files are preserved in `Original_Game_Files`.
The build process makes a separate copy of `p6.py` and adds only a small startup-path adjustment
so bundled files can be found inside the app bundle. `background.JPG` is copied as
`background.jpg` in the build staging area because the original program requests the lowercase
filename. This avoids relying on the Mac disk's case-sensitivity setting.

No gameplay changes are made by this packaging step.
