#!/usr/bin/env python3
"""Bulk download Momentum wallpapers from all available sources."""

import os
import sys
import json
import time
from datetime import datetime, timedelta

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

DIR = os.path.dirname(os.path.realpath(__file__))
PICTURES = os.path.join(DIR, 'pictures')
STATE_FILE = os.path.join(DIR, '.sync_state.json')
ARCHIVE_INTERVAL_DAYS = 20
CATEGORIES = ['morning', 'afternoon', 'evening', 'night']
ARCHIVE_PER_CATEGORY = 20


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {'last_api_sync': None, 'archive_complete': False}


def save_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except OSError as e:
        print(f'  Failed to save sync state: {e}', file=sys.stderr)


def archive_complete():
    for cat in CATEGORIES:
        for i in range(1, ARCHIVE_PER_CATEGORY + 1):
            path = os.path.join(PICTURES, f'{cat}_{i:02d}.jpg')
            if not os.path.exists(path):
                return False
    return True


def should_sync_api(state):
    if not state.get('archive_complete'):
        return True
    last = state.get('last_api_sync')
    if last is None:
        return True
    try:
        last_dt = datetime.strptime(last, '%Y-%m-%d')
        return (datetime.now() - last_dt).days >= ARCHIVE_INTERVAL_DAYS
    except ValueError:
        return True


def next_sync_date(state):
    last = state.get('last_api_sync')
    if last is None:
        return 'now'
    try:
        last_dt = datetime.strptime(last, '%Y-%m-%d')
        next_dt = last_dt + timedelta(days=ARCHIVE_INTERVAL_DAYS)
        return next_dt.strftime('%Y-%m-%d')
    except ValueError:
        return 'unknown'


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
    except (URLError, OSError) as e:
        print(f'  FAILED: {url} - {e}')
        return False


def source_api(state):
    """Download current backgrounds from the Momentum API."""
    if not should_sync_api(state):
        print(f'  Skipped (next API sync: {next_sync_date(state)})')
        return False

    try:
        from config import client_id
    except ImportError:
        print('config.py not found. Run install.sh first.')
        return False

    today = time.strftime('%Y-%m-%d')
    req = Request(f'https://api.momentumdash.com/feed/bulk?syncTypes=backgrounds&localDate={today}')
    req.add_header('Accept', '*/*')
    req.add_header('X-Momentum-ClientId', client_id)
    req.add_header('X-Momentum-Version', '0.91.1')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')

    try:
        resp = urlopen(req, timeout=30)
        data = json.loads(resp.read())
    except (URLError, HTTPError, json.JSONDecodeError) as e:
        print(f'API error: {e}')
        return False

    for bg in data.get('backgrounds', []):
        name = bg.get('filename', '').rsplit('/', 1)[-1]
        if not name:
            continue
        path = os.path.join(PICTURES, name)
        print(f'  {name}')
        download(bg['filename'], path)

    state['last_api_sync'] = today
    state['archive_complete'] = archive_complete()
    save_state(state)
    return True


def source_olmeor():
    """Download the archived Momentum collection from Olmeor's GitHub repo."""
    base = 'https://raw.githubusercontent.com/Olmeor/momentum-backgrounds/main'

    for cat in CATEGORIES:
        for i in range(1, ARCHIVE_PER_CATEGORY + 1):
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

    print('  Scanning past dates for wallpapers (this may take a while)...')
    found = 0

    for offset in range(1, 1500, 7):
        d = (datetime.now() - timedelta(days=offset)).strftime('%Y-%m-%d')
        req = Request(f'https://api.momentumdash.com/feed/bulk?syncTypes=backgrounds&localDate={d}')
        req.add_header('Accept', '*/*')
        req.add_header('X-Momentum-ClientId', client_id)
        req.add_header('X-Momentum-Version', '0.91.1')
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        try:
            resp = urlopen(req, timeout=15)
            data = json.loads(resp.read())
            for bg in data.get('backgrounds', []):
                name = bg.get('filename', '').rsplit('/', 1)[-1]
                if not name:
                    continue
                path = os.path.join(PICTURES, name)
                if not os.path.exists(path):
                    print(f'  [{d}] {name} - {bg.get("title", "?")}')
                    download(bg['filename'], path)
                    found += 1
        except (URLError, HTTPError, json.JSONDecodeError) as e:
            print(f'  [{d}] skip: {e}', file=sys.stderr)
        time.sleep(0.5)

    print(f'  Found {found} new wallpapers from past dates.')


def main():
    state = load_state()

    sources = [
        ('Momentum API (current backgrounds)', lambda: source_api(state)),
        ('Olmeor GitHub archive (80 classic wallpapers)', source_olmeor),
    ]

    print('Starting bulk download...\n')
    os.makedirs(PICTURES, exist_ok=True)
    total_before = len([f for f in os.listdir(PICTURES) if os.path.isfile(os.path.join(PICTURES, f))])

    for label, func in sources:
        print(f'[{label}]')
        func()
        print()

    total_after = len([f for f in os.listdir(PICTURES) if os.path.isfile(os.path.join(PICTURES, f))])
    new_count = total_after - total_before

    print(f'Done. {new_count} new wallpapers downloaded, {total_after} total in pictures/')

    if state.get('archive_complete') and state.get('last_api_sync'):
        print(f'Next API sync scheduled after: {next_sync_date(state)}')


if __name__ == '__main__':
    main()
