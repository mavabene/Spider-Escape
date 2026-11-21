# Spider Escape project log

## 2026-11-15 18:59 PST

TL;DR: Released the version 2.0 Mac build and started a feature backlog.

Updated the maintained regular and easy game code with timed Spanish questions, a persistent high score, resized and mirrored spiders, rotated splats, opacity variation, and fading tire tracks. Updated the Apple Silicon build process and produced the 2.0 app and ZIP. Added planned gameplay and customization ideas to TODO.md.

Next step / open issues: Play-test version 2.0; backlog items remain open.

## 2026-11-15 21:48 PST

TL;DR: Rebuilt the Mac app as 2.0.1 for sharing and archived it with a playable original version.

Rebuilt outside iCloud, locally signed the app, and verified its signature after extracting the delivery ZIP. One recipient confirmed the new version opens. Archived immutable copies of the 2.0.1 and original Mac apps in Distribution with SHA-256 checksums. Added backlog ideas for collectible bug-zapper ammo and power-ups.

Next step / open issues: Confirm the 2.0.1 ZIP opens on the remaining recipient's Mac; Apple notarization remains an option for wider distribution.

## 2026-11-18 21:30 PST

**TL;DR** Saved the untracked trial game with two-player options and collectible effects.

Added the trial source, rules, README, and Mac build script to version control. The trial includes player/color/quiz options, pickup-based ammo, armor, slow, repellent, and separate trial scores. Python syntax, rule behavior, and build-script syntax checks passed; interactive gameplay and a fresh app build were not verified in this update.

**Next step / open issues** Play-test the trial and verify a fresh Mac build; reconcile the iCloud checkout with the existing local copy before migrating.

## 2026-11-19 23:04 PST

**TL;DR** Saved the 2.0.2 trial menu, zapper recharge, pickup icons, and tire-track improvements.

Updated the clickable start menu, ten-second zapper charging, illustrated pickups, roadside foliage, splat sizing, and per-tire fading tracks. Renamed the trial build to 2.0.2. Python and shell syntax, headless menu rendering, and zapper recharge checks passed.

**Next step / open issues** Play-test the revised trial and verify a fresh Mac app build; reconcile the existing local and iCloud copies before migration.

## 2026-11-20 21:13 PST

**TL;DR** Updated the 2.0.2 trial with armor impacts, natural spider colors, a wider co-op playfield, and a launchable Mac app in Trial.

Armored cars splat small spiders, shove larger ones aside, and slow briefly on impact with the largest quarter. Brown and gray spiders predominate, both cars default to Original, and two-player mode uses 1280 × 800. Incorporated the compact two-column options panel from iCloud. Rebuilt, signed, and verified the Mac app in `Trial`. Collision, palette, and headless display checks passed.

**Next step / open issues** Play-test the updated trial interactively. The iCloud checkout still has its original menu edit; use the local checkout for the current app.


## 2026-11-20 22:07 PST

**TL;DR** Saved the current Spider Escape build as the 2.0.2 Mac release.

Archived the read-only release ZIP in iCloud Distribution and recorded its SHA-256 checksum. Verified the extracted app’s signature and matched it to the installed build. The release adds denser, drive-under bushes, a rare flamethrower with per-player fuel gauges, shield expiry colors, wider solo play, menu scores, and a five-second collision freeze.

**Next step / open issues** Play-test the release on both Macs. The Git checkout on this Mac is still in iCloud.
