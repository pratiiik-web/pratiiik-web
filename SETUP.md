# GitHub profile kit

Recreates the "terminal card + radar charts + live stats" profile style.

## Setup (5 minutes)

1. On GitHub, create a **public repo named exactly your username** (e.g. `pratik-karale/pratik-karale`) and tick "Add a README".
2. Copy everything in this folder into that repo (keep the `.github/` folder).
3. Edit `config.json`: set `username`, the card rows, and the radar scores (be honest, it reads better).
4. Edit `README.template.md` for your own bio text. Leave `{{username}}` as is.
5. Repo **Settings → Actions → General → Workflow permissions**: choose "Read and write permissions".
6. **Actions** tab → `refresh-profile` → **Run workflow**. It generates `assets/*.svg` and `README.md` and commits them.
7. Optional: create a classic personal access token with `read:user` scope, save it as repo secret `PROFILE_TOKEN`. This unlocks the contributions and streak numbers; without it they show "–".

## Preview locally

```bash
python scripts/generate.py     # uses GITHUB_TOKEN if set
```

Open `assets/terminal.svg` in a browser to check it.

## Optional dithered portrait

```bash
pip install pillow
python scripts/portrait.py my-photo.jpg
```

Then add `<img src="assets/portrait.svg" width="300" />` to `README.template.md`.
Use a high-contrast, plain-background photo for the best result.

## Notes

- `README.md` is generated. Edit `README.template.md`, not `README.md`.
- Radar scores are self-ratings you set in `config.json`, not measured.
