# Momentum Desktop Wallpaper Linux

Downloads the Momentum daily backgrounds to your computer and optionally sets them as your desktop wallpaper.

## Requirements

- Python 3
- systemd (optional, for automatic wallpaper switching)

## Installation

    git clone https://github.com/moin-ek/momentum-desktop-wallpaper-linux.git
    cd momentum-desktop-wallpaper-linux
    ./install.sh

## Uninstallation

    ./uninstall.sh

## Manual Run

    python3 sync_momentum.py

## Errors

Run the script directly to see any potential errors.

### 400 Bad Request
Usually means your client ID is wrong or not recognised.

### HTTP Error 403: Forbidden
Make sure you are using a valid client ID.
