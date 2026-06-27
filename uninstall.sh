#!/bin/sh
set -e

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
  printf "\n${RED}╔══════════════════════════════════════════════════╗${NC}\n"
  printf "${RED}║${NC}  ${BOLD}Momentum Desktop Wallpaper — Uninstaller${NC}    ${RED}║${NC}\n"
  printf "${RED}╚══════════════════════════════════════════════════╝${NC}\n\n"
}

info()  { printf "${CYAN}::${NC} ${BOLD}%s${NC}\n" "$1"; }
step()  { printf "  ${GREEN}✓${NC} %s\n" "$1"; }
warn()  { printf "  ${YELLOW}⚠${NC} %s\n" "$1" >&2; }
dim()   { printf "  ${DIM}%s${NC}\n" "$1"; }

# ═══════════════════════════════════════════════════════════════
header

if [ -z "${HOME}" ]; then
  printf "  ${RED}✗${NC} \$HOME is not set — aborting.\n" >&2
  exit 1
fi

info "Removing systemd timer and service"
echo

if command -v systemctl >/dev/null 2>&1; then
  systemctl --user disable --now momentum-sync.timer 2>/dev/null || true
  step "Timer disabled"
  rm -f "${HOME}/.config/systemd/user/momentum-sync.service"
  step "Service file removed"
  rm -f "${HOME}/.config/systemd/user/momentum-sync.timer"
  step "Timer file removed"
  systemctl --user daemon-reload
  step "Systemd daemon reloaded"
else
  rm -f "${HOME}/.config/systemd/user/momentum-sync.service"
  rm -f "${HOME}/.config/systemd/user/momentum-sync.timer"
  step "Service & timer files removed (systemctl not found)"
fi

echo
printf "\n${GREEN}╔══════════════════════════════════════════════════╗${NC}\n"
printf "${GREEN}║${NC}  ${BOLD}Uninstall complete.${NC}                               ${GREEN}║${NC}\n"
printf "${GREEN}╚══════════════════════════════════════════════════╝${NC}\n"
printf "\n"
dim "Wallpapers and config are still on disk."
dim "Remove them manually if desired:"
dim "  rm -rf pictures/ config.py .sync_state.json"
echo
