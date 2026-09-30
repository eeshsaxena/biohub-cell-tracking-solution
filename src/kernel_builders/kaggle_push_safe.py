"""Run `kaggle kernels push` with a working slugify.

A Python-2 era `slugify.py` in site-packages shadows python-slugify and crashes the CLI with
NameError: unicode. Patch the name inside the kaggle module only; the environment is untouched.
usage: python kaggle_push_safe.py <kernel folder>
"""
import os
import re
import sys

# the script directory holds a folder that shadows the kaggle package
_here = os.path.dirname(os.path.abspath(__file__))
sys.path = [x for x in sys.path if os.path.abspath(x or ".") != _here]

import kaggle  # noqa: F401  (initialises + authenticates; importing the submodule first is circular)

ext = sys.modules["kaggle.api.kaggle_api_extended"]
from kaggle.cli import main


def _slugify(text, *args, **kwargs):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


ext.slugify = _slugify
sys.argv = ["kaggle", "kernels", "push", "-p", os.path.abspath(sys.argv[1])]
main()
