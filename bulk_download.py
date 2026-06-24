#!/usr/bin/env python3
"""Bulk download Momentum wallpapers from all available sources."""

import os
import json
import time

from urllib.request import Request, urlopen

DIR = os.path.dirname(os.path.realpath(__file__))
PICTURES = os.path.join(DIR, 'pictures')
os.makedirs(PICTURES, exist_ok=True)

def download(url, path, referer=None):
    if os.path.exists(path):
        return False
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
    if referer:
        req.add_header('Referer', referer)
    try:
        data = urlopen(req, timeout=30).read()
        with open(path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f'  FAILED: {url} - {e}')
        return False

def source_api():
    """Download current backgrounds from the Momentum API."""
    try:
        from config import client_id
    except ImportError:
        print('config.py not found. Run install.sh first.')
        return

    today = time.strftime("%Y-%m-%d")
    req = Request(f'https://api.momentumdash.com/feed/bulk?syncTypes=backgrounds&localDate={today}')
    req.add_header('Accept', '*/*')
    req.add_header('X-Momentum-ClientId', client_id)
    req.add_header('X-Momentum-Version', '0.91.1')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')

    try:
        resp = urlopen(req)
        data = json.loads(resp.read())
    except Exception as e:
        print(f'API error: {e}')
        return

    for bg in data.get('backgrounds', []):
        name = bg['filename'].rsplit('/', 1)[-1]
        path = os.path.join(PICTURES, name)
        print(f'  {name}')
        download(bg['filename'], path)

def source_olmeor():
    """Download the archived Momentum collection from Olmeor's GitHub repo."""
    base = 'https://raw.githubusercontent.com/Olmeor/momentum-backgrounds/main'
    categories = ['morning', 'afternoon', 'evening', 'night']

    for cat in categories:
        for i in range(1, 21):
            name = f'{i:02d}.jpg'
            url = f'{base}/{cat}/{name}'
            saved_name = f'{cat}_{name}'
            path = os.path.join(PICTURES, saved_name)
            saved = download(url, path)
            if saved:
                print(f'  {cat}/{name}')

def source_discover():
    """Discover additional backgrounds by querying past dates via API."""
    try:
        from config import client_id
    except ImportError:
        return

    today = time.strftime("%Y-%m-%d")
    year = int(today[:4])

    for offset in range(1, 1500, 7):
        from datetime import datetime, timedelta
        d = (datetime.now() - timedelta(days=offset)).strftime('%Y-%m-%d')
        req = Request(f'https://api.momentumdash.com/feed/bulk?syncTypes=backgrounds&localDate={d}')
        req.add_header('Accept', '*/*')
        req.add_header('X-Momentum-ClientId', client_id)
        req.add_header('X-Momentum-Version', '0.91.1')
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        try:
            resp = urlopen(req)
            data = json.loads(resp.read())
            for bg in data.get('backgrounds', []):
                name = bg['filename'].rsplit('/', 1)[-1]
                path = os.path.join(PICTURES, name)
                if not os.path.exists(path):
                    print(f'  [{d}] {name} - {bg.get("title", "?")}')
                    download(bg['filename'], path)
        except Exception:
            pass

def main():
    sources = [
        ('Momentum API (current backgrounds)', source_api),
        ('Olmeor GitHub archive (80 classic wallpapers)', source_olmeor),
    ]

    print('Starting bulk download...\n')
    total_before = len([f for f in os.listdir(PICTURES) if os.path.isfile(os.path.join(PICTURES, f))])

    for label, func in sources:
        print(f'[{label}]')
        func()
        print()

    total_after = len([f for f in os.listdir(PICTURES) if os.path.isfile(os.path.join(PICTURES, f))])
    new_count = total_after - total_before

    print(f'Done. {new_count} new wallpapers downloaded, {total_after} total in pictures/')

if __name__ == '__main__':
    main()
