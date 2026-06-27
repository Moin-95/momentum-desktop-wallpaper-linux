[Unit]
Description=Momentum wallpaper sync and switch
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart={CURR_DIR}/switch_wallpaper.sh
WorkingDirectory={CURR_DIR}
StandardOutput=journal
StandardError=journal
