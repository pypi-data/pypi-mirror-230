import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pytest
import sys
from pathlib import Path

import pkg_resources

main_folder = Path(__file__).parent.parent
sys.path.insert(0, str(main_folder))
sys.path.insert(0, str(main_folder / 'jetdnn'))
sys.path.insert(0, str(main_folder / 'tests'))
os.chdir(main_folder / 'jetdnn')

import jetdnn