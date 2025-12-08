# -*- coding: utf-8 -*-
"""
Main file of the python script for WP4.
"""

import sys
from pathlib import Path
import Calculations
# project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from UX import ui   # change lug_ui to your actual UI module name


def main():
    app = ui.LugToolUI()
    app.mainloop()




import yaml
from pathlib import Path
import Calculations.stuff as stuff  # where your run_all() or similar lives

def main2():

    # path to your dict file
    dict_path = Path("./Data/Dicts.yaml")

    with dict_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # unpack
    try:
        config = data["config"]
        geometry = data["geometry"]
        loads = data["loads"]
    except KeyError as e:
        raise KeyError(f"Missing required key in Dicts.yaml: {e}")
    print(config)
    # call your calculation function
    # replace Calculations.stuff.run_all with the real target function
    result = stuff.run_it(config, geometry, loads,"./Data/lug_scan.npz")

    return result

if __name__ == "__main__":
    main()
