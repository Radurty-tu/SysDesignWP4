# -*- coding: utf-8 -*-
"""
Main file of the python script for WP4.
"""

import sys
from pathlib import Path

# project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from UX import ui   # change lug_ui to your actual UI module name


def main():
    app = ui.LugToolUI()
    app.mainloop()


if __name__ == "__main__":
    main()
