"""Makes ``python -m cli`` behave the same as the ``ledger`` launcher."""

import sys

from cli import main

sys.exit(main())
