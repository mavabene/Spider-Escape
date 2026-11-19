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
