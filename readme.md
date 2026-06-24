# Momentum Desktop Images

Downloads the Momentum daily backgrounds to your computer and optionally sets them as your desktop wallpaper.

## Installation

    git clone https://github.com/mattbryson/momentum-desktop-images.git
    cd momentum-desktop-images
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
