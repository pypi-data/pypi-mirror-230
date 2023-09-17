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

"""
Assumes that test_predict is successful.
"""

def test_get_equation():

    csv = "table_EUROfusion_db_JSimpson_24april2019_D_withpellets_normp_nokikcs_only_validated.dat"
    csv_path = os.path.abspath("../" + csv)

    input_cols = ["Ip (MA)","P_tot (MW)","B (T)"]
    real_output_col = ["Te ped height pre-ELM (keV)"]
    test_data = jetdnn.predict.build_and_test_single(csv_path,input_cols,real_output_col)[3]
    testinput = test_data[input_cols]

    model, output_expected, error, data = jetdnn.predict.build_and_test_single(csv_path,input_cols,real_output_col)

    output_expected = np.array(output_expected)
    output = np.array(jetdnn.visualise.get_equation(model,data,input_cols,real_output_col)[2]).flatten()

    #print(jetdnn.visualise.get_equation(model,csv_path,input_cols,real_output_col)[0])

    assert output == pytest.approx(output_expected,abs=0.8) # checks that the output of the neural network checks out with the tensorflow predicted values