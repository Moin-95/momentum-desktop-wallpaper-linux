#!/bin/sh
set -e

CURR_DIR=$(pwd)

# ── color definitions ──────────────────────────────────────────
BOLD='\033[1m'
DIM='\033[2m'
BLUE='\033[1;34m'
CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
GREY='\033[0;37m'
NC='\033[0m'

# ── helpers ────────────────────────────────────────────────────
header() {
  printf "\n${BLUE}╔══════════════════════════════════════════════════╗${NC}\n"
  printf "${BLUE}║${NC}  ${BOLD}Momentum Desktop Wallpaper — Installer${NC}      ${BLUE}║${NC}\n"
  printf "${BLUE}╚══════════════════════════════════════════════════╝${NC}\n\n"
}

info()  { printf "${CYAN}::${NC} ${BOLD}%s${NC}\n" "$1"; }
step()  { printf "  ${GREEN}✓${NC} %s\n" "$1"; }
warn()  { printf "  ${YELLOW}⚠${NC} %s\n" "$1" >&2; }
err()   { printf "  ${RED}✗${NC} %s\n" "$1" >&2; }
dim()   { printf "  ${DIM}%s${NC}\n" "$1"; }

# ═══════════════════════════════════════════════════════════════
header

info "Step 1  —  Momentum Client ID"
echo
dim "To find your ID:"
dim "  1. Open Chrome / Momentum Dashboard"
dim "  2. Click the settings cog (bottom-left)"
dim "  3. Click About"
dim "  4. Double-click the version number"
dim "  5. Copy the ID that appears"
echo
printf "  ${BOLD}Paste your Client ID:${NC} "
read -r client_id

if [ -z "$client_id" ]; then
  err "No Client ID entered — aborting."
  exit 1
fi

printf "client_id='%s'\n" "$client_id" > config.py
step "Client ID saved to config.py"
echo

# ═══════════════════════════════════════════════════════════════
info "Step 2  —  Automatic Wallpaper Switching"
echo
dim "A systemd timer will switch wallpapers 4x daily:"
dim "  morning  (08:00)   │  noon    (12:00)"
dim "  evening  (20:00)   │  night   (23:00)"
dim "Each run picks a wallpaper matching the time of day."
echo
printf "  ${BOLD}Set up automatic switching?${NC} ${DIM}[y/N]${NC} "
read -r auto

if [ "$auto" = "y" ] || [ "$auto" = "Y" ]; then
  if command -v systemctl >/dev/null 2>&1; then
    SYSTEMD_DIR="${HOME}/.config/systemd/user"
    mkdir -p "$SYSTEMD_DIR"
    sed "s|{CURR_DIR}|$CURR_DIR|g" "$CURR_DIR/download_agent/momentum-sync.service.tpl" > "$SYSTEMD_DIR/momentum-sync.service"
    cp "$CURR_DIR/download_agent/momentum-sync.timer" "$SYSTEMD_DIR/momentum-sync.timer"
    systemctl --user daemon-reload
    systemctl --user enable --now momentum-sync.timer
    step "Timer enabled — next run at the next scheduled time"
  else
    warn "systemctl not found — skipping timer setup"
  fi
else
  dim "(skipped)"
fi
echo

# ═══════════════════════════════════════════════════════════════
info "Step 3  —  Downloading Wallpapers"
echo
python3 "$CURR_DIR/bulk_download.py"

echo
# ═══════════════════════════════════════════════════════════════
printf "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}\n"
printf "${GREEN}║${NC}  ${BOLD}All done!${NC}                                          ${GREEN}║${NC}\n"
printf "${GREEN}╚══════════════════════════════════════════════════╝${NC}\n"
printf "\n"
dim "Manual run:          python3 sync_momentum.py"
dim "Uninstall:           ./uninstall.sh"
dim "Bulk re-download:    python3 bulk_download.py"
echo
