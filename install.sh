#!/usr/bin/env bash
# Install the gameplay-vertical-short skill for an agent.
#   ./install.sh               Claude Code   (~/.claude/skills/gameplay-vertical-short)
#   ./install.sh --codex       Codex         (~/.codex/skills/gameplay-vertical-short)
#   ./install.sh --agents      shared agents (~/.agents/skills/gameplay-vertical-short)
#   ./install.sh --dir PATH    any skills folder
# An existing copy is moved to ~/.local/share/gameplay-vertical-short/backups/<time>, never overwritten
# (outside the skills folder, so agents don't load the backup as a second skill).
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
  "") BASE="$HOME/.claude/skills" ;;
  --codex) BASE="$HOME/.codex/skills" ;;
  --agents) BASE="$HOME/.agents/skills" ;;
  --dir) BASE="${2:?--dir needs a path}" ;;
  *) echo "unknown option: $1 (see the top of install.sh)" >&2; exit 1 ;;
esac
DEST="$BASE/gameplay-vertical-short"
mkdir -p "$BASE"
if [ -e "$DEST" ]; then
  BACKUP="${GVS_BACKUP_DIR:-$HOME/.local/share/gameplay-vertical-short/backups}/$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$(dirname "$BACKUP")"
  mv "$DEST" "$BACKUP"
  echo "existing skill moved to $BACKUP"
fi
mkdir -p "$DEST"
cp -R SKILL.md tools examples "$DEST/"
chmod +x "$DEST/tools/"*.sh
echo "installed to $DEST"
command -v ffmpeg >/dev/null || echo "note: ffmpeg is not on PATH; install it (see README)"
python3 -c "import numpy, scipy, soundfile" 2>/dev/null || echo "note: run 'python3 -m pip install -r requirements.txt' for the score"
