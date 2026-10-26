"""Lets ``python -m cli`` run the ledger, the same entry point the ``ledger`` launcher uses."""

import sys

from cli import main

sys.exit(main())
