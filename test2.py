#!/usr/bin/env python

import sys

for line in sys.stdin:
    print(line.upper(), end='', flush=True)