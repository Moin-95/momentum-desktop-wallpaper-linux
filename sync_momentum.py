#!/usr/bin/env python3

import os
import sys
import json
import time

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

try:
    from config import client_id
except ImportError:
    print('config.py not found. Run install.sh first.', file=sys.stderr)
    sys.exit(1)

def main():
    directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pictures')
    today = time.strftime("%Y-%m-%d")

    req = Request('https://api.momentumdash.com/feed/bulk?syncTypes=backgrounds&localDate=' + today)
    req.add_header('Host', 'api.momentumdash.com')
    req.add_header('Accept', '*/*')
    req.add_header('X-Momentum-ClientId', client_id)
    req.add_header('X-Momentum-Version', '0.91.1')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')

    try:
        response = urlopen(req, timeout=30)
        data = json.loads(response.read())
    except HTTPError as e:
        print(f'API HTTP error: {e.code} {e.reason}', file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f'API connection error: {e.reason}', file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, ValueError) as e:
        print(f'API response parse error: {e}', file=sys.stderr)
        sys.exit(1)

    os.makedirs(directory, exist_ok=True)

    for bg in data.get('backgrounds', []):
        name = bg.get('filename', '').rsplit('/', 1)[-1]
        if not name:
            continue
        path = os.path.join(directory, name)
        print(name)
        if not os.path.exists(path):
            img_req = Request(bg['filename'])
            img_req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            try:
                img_data = urlopen(img_req, timeout=30).read()
                with open(path, 'wb') as f:
                    f.write(img_data)
            except (URLError, OSError) as e:
                print(f'  FAILED: {name} - {e}', file=sys.stderr)

if __name__ == '__main__':
    main()
