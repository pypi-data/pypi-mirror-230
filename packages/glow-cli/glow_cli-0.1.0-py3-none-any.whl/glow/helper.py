"""
Helper functions for glow
Needs to be as tiny as possible
"""


import sys
from subprocess import run


def run_command(cmd: str) -> None:
    """
    Run a shell command and collect results
    """
    return run(cmd, shell=True,
               stdout=sys.stdout, stderr=sys.stderr,
               executable='/bin/bash',
               )
