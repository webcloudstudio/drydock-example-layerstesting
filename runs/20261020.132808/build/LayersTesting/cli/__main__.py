"""Lets ``python -m cli`` run the same entry point the ``ledger`` launcher uses."""

import sys

from cli import main

sys.exit(main())
