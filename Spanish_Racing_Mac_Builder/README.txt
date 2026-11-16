Spider Escape 2.0.1 — Mac build

Run Build_Mac.command to build the maintained regular game from ../Finalp6/p6.py.
The script uses .venv-arm64 and packages the game with its artwork, audio, and fonts.

Outputs:
  Verified app in the temporary build folder printed by the script
  Spider Escape-2.0.1-Mac.zip

Version 2.0 includes a ten-second Spanish quiz countdown, persistent high score,
resized and mirrored spiders, rotated splats, and fading red tire marks. Spider
sizes vary from 0.5x to 1.5x with a distribution centered at 1x. Splat opacity
varies from 50% to 100%, weighted toward opaque. Tire marks inherit splat color
and opacity and fade over a random half to one car length. Spider collisions use
the visible silhouette.

The high score is stored in ~/Library/Application Support/Spider Escape/high_score.json.
Original_Game_Files contains the archived original code and assets.

This app has a local signature but is not Apple-notarized. On first launch,
macOS may require System Settings > Privacy & Security > Open Anyway.

Packaging update 2.0.1 builds outside iCloud, signs the app locally, and verifies
the signature again after extracting the delivered ZIP. It is not notarized.
Recipients should replace older copies, extract the ZIP, move the app to Applications,
try opening it, then use System Settings > Privacy & Security > Open Anyway if offered.
