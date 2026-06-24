#!/bin/sh
DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$DIR/sync_momentum.py"

HOUR=$(date +%H)

if [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 12 ]; then
  period="morning"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 17 ]; then
  period="afternoon"
elif [ "$HOUR" -ge 17 ] && [ "$HOUR" -lt 21 ]; then
  period="evening"
else
  period="night"
fi

img=$(find "$DIR/pictures" -type f -name "${period}_*" 2>/dev/null | shuf -n1)

if [ -z "$img" ]; then
  img=$(find "$DIR/pictures" -type f 2>/dev/null | shuf -n1)
fi

if [ -z "$img" ]; then
  printf "No images found in pictures/ directory.\n" >&2
  exit 1
fi

if command -v plasma-apply-wallpaperimage &>/dev/null; then
  plasma-apply-wallpaperimage "$img"
elif command -v gsettings &>/dev/null; then
  gsettings set org.gnome.desktop.background picture-uri "file://${img}"
  gsettings set org.gnome.desktop.background picture-uri-dark "file://${img}"
elif command -v feh &>/dev/null; then
  feh --bg-fill "$img"
elif command -v xwallpaper &>/dev/null; then
  xwallpaper --zoom "$img"
else
  printf "No supported wallpaper tool found. Apply manually:\n  %s\n" "$img"
fi
