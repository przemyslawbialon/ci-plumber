#!/usr/bin/env python3

import os
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ci_plumber import CIPlumber


def main():
    config_path = os.path.join(os.path.dirname(__file__), "..", "cfg", "config.yaml")
    plumber = CIPlumber(config_path)
    plumber.run()


if __name__ == "__main__":
    main()
