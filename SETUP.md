# Setup

1. Extract everything into the root of `meadowlys/meadowlys`. Replace the old README; remove old unused assets and disable the old widget workflow if present.
2. Commit the README, assets, scripts and hidden `.github` directory. If uploading through the web UI, verify `.github/workflows/profile.yml` is present afterwards.
3. Go to Actions > Update profile widgets > Run workflow. If disabled, enable Actions first. Repository settings > Actions > General must allow the workflow to write repository contents.
4. The initial repository panel is a plain local fallback. The first successful workflow fetches original game screenshots, boat footage, public repository data and renders a monochrome animated panel. If the video fails, it uses the real Start Screen still; if both fail, the run fails without replacing the existing panel. No token setup needed for public repo REST data. The optional contribution GraphQL query may fail depending on permissions; this does not prevent the main widget from updating.

To run locally, install Python, Pillow, FFmpeg and DejaVu fonts, then run `python scripts/build.py --online` (the renderer uses Linux font paths). `python scripts/build.py` renders the offline fallback only. No custom JS runs in GitHub README images. Each row's background thumbnail is game imagery, not a screenshot of the repository. The entire menu links to the repo list and actual project links appear below it after the workflow runs.

Game assets copyright their respective owners. Source links in SOURCES.md. The game menu is adapted to GitHub data; it is not the original executable UI. External media/statistics may be unavailable. Age is shown at your request; remove it if you don't want it public.
