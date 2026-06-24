systemctl --user disable --now momentum-sync.timer 2>/dev/null
rm -f "${HOME}/.config/systemd/user/momentum-sync.service"
rm -f "${HOME}/.config/systemd/user/momentum-sync.timer"
systemctl --user daemon-reload
