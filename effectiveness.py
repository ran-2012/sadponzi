#!/usr/bin/python3 -u

import os
import subprocess
import sys

def process(cmd, shell=False):
    if isinstance(cmd, str):
        cmd = cmd.split(' ')
    return subprocess.run(cmd, shell=shell)

if len(sys.argv) != 2:
    print('Usage: %s [flags] <path_to_dataset>' % sys.argv[0], file=sys.stderr)
    exit(0)

for sampe_path in os.listdir(sys.argv[1]):
    cmd = 'python3  -i {} -o {} -b {} -r {}'.format(input_, output, args.browser, args.ref)
    process(cmd)
            