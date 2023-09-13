import os
import subprocess  # nosec
import sys


def run():
    sys.exit(subprocess.call([ # nosec
        os.path.join(os.path.dirname(__file__), 'bauplan-cli'),
        *sys.argv[1:]
    ]))


if __name__ == '__main__':
    run()
