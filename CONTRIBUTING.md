# Contributing

Thanks for helping! Fixes, presets for more games (minimap boxes, HUD crops), palettes, docs and
translations of the publish-kit guidance are all welcome.

## Ground rules

- **Local and free.** No paid APIs, accounts or network calls in the tools.
- **No copyrighted media.** Don't add music, sound effects, fonts or game footage to the repo. Sound
  effects stay in the user's own library (`GVS_SFX_DIR`).
- **Never post or upload** on the user's behalf.
- **Facts from the footage.** Changes to `SKILL.md` must keep the rule that every caption claim is
  checked against a frame.

## Develop

```bash
python3 -m pip install -r requirements.txt
tests/smoke.sh            # renders a short end to end from synthetic footage and checks size, fps, length, loudness
```

Keep the tools small and readable, with a docstring that shows usage. Read machine-specific settings
from environment variables through `tools/gvs.py`, never from hard-coded paths. Check with
`git status` that you aren't committing footage, renders or personal paths.

## Pull requests

Describe what changed and how you tested it (attach a frame strip for visual changes, made from
footage you have the rights to share), and add a line to `CHANGELOG.md` under *Unreleased*.

By contributing you agree that your work is released under the [MIT License](LICENSE).
