#!/usr/bin/env python3

import os
import sys
import json
import time

from urllib.request import Request, urlopen

from config import *

directory = os.path.dirname(os.path.realpath(__file__)) + '/pictures/'
today = time.strftime("%Y-%m-%d")

req = Request('https://api.momentumdash.com/feed/bulk?syncTypes=backgrounds&localDate=' + today)
req.add_header('Host', 'api.momentumdash.com')
req.add_header('Accept', '*/*')
req.add_header('X-Momentum-ClientId', client_id)
req.add_header('X-Momentum-Version', '0.91.1')
req.add_header('Content-Type', 'application/json')
req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')

response = urlopen(req)
data = json.loads(response.read())

if not os.path.exists(directory):
    os.makedirs(directory)

for bg in data['backgrounds']:
    name = bg['filename'].rsplit('/', 1)[-1]
    path = os.path.join(directory, name)
    print(name)
    if not os.path.exists(path):
        img_req = Request(bg['filename'])
        img_req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        img_data = urlopen(img_req).read()
        with open(path, 'wb') as f:
            f.write(img_data)
