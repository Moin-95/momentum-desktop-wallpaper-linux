CURR_DIR=$(pwd)

BLUE='\033[1;34m'
GREY='\033[0;37m'
NC='\033[0m'

printf "${BLUE}This will set up momentum_sync for you.${NC}\n\n"
printf "First you need to get your momentum client ID\n\n"
printf "1. In Chrome / Momentum click on the settings cog bottom left\n"
printf "2. Click on About\n"
printf "3. Double click on the version number under the momentum logo\n"
printf "4. Copy the ID that is then shown\n"
printf "5. Paste it below...\n"

read client_id

printf "client_id='%s'\n" "$client_id" > config.py

printf "\n\nGreat, now you can manually run with the command 'python3 ./sync_momentum.py'\n\n"
printf "${BLUE}Would you like to set up automatic wallpaper switching?${NC}\n"
printf "${GREY}This runs 3x daily (08:00, 13:00, 20:00) and picks a\nwallpaper matching the time of day.${NC}\n"
printf "${GREY}You can remove this with ./uninstall.sh later${NC}\n"
printf "y/n? "

read auto

if [ "$auto" = "y" ]; then
  SYSTEMD_DIR="${HOME}/.config/systemd/user"
  mkdir -p "$SYSTEMD_DIR"
  sed "s|{CURR_DIR}|$CURR_DIR|g" download_agent/momentum-sync.service.tpl > "$SYSTEMD_DIR/momentum-sync.service"
  cp download_agent/momentum-sync.timer "$SYSTEMD_DIR/momentum-sync.timer"
  systemctl --user daemon-reload
  systemctl --user enable --now momentum-sync.timer
fi

printf "syncing pictures...\n"
python3 ./sync_momentum.py

printf "\nYour all done\n"
printf "${GREY}To uninstall you can run ./uninstall.sh${NC}\n"
