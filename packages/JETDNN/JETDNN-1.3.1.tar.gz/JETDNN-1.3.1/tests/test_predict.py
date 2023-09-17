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

# DNN TESTING FUNCTIONS
"""
The error provided is the error found for temperature data in the dataset used for "On neutral ground: can neutrals influence plasma pedestal formation?" by S. Frankel, J. Simpson and E. Solano
It is suggested to use this dataset or temperature pedestal data for testing with the below functions.

Assumes that test_data_manip is successful.
"""

test_csv = "table_EUROfusion_db_JSimpson_24april2019_D_withpellets_normp_nokikcs_only_validated.dat"
df = pd.read_csv(os.path.abspath("../" + test_csv),sep="\s{3,}|\s{3,}|\t+|\s{3,}\t+|\t+\s{3,}",skipinitialspace=True)
print(df.columns)

def test_build_and_test_single():

    csv = "table_EUROfusion_db_JSimpson_24april2019_D_withpellets_normp_nokikcs_only_validated.dat"
    csv_path = os.path.abspath("../" + csv)

    input_cols = ["Ip (MA)","P_tot (MW)","B (T)"]
    real_output_col = ["Te ped height pre-ELM (keV)"]

    test_data = jetdnn.predict.build_and_test_single(csv_path,input_cols,real_output_col)[3]
    output_expected = test_data[real_output_col].values.flatten().tolist()
    output = jetdnn.predict.build_and_test_single(csv_path,input_cols,real_output_col)[1] # returns flat_ped, or the predictions

    assert output == pytest.approx(output_expected,abs=0.7) # 0.7 found to be the absolute error with testing

def test_predict_single():
    
    csv = "table_EUROfusion_db_JSimpson_24april2019_D_withpellets_normp_nokikcs_only_validated.dat" # can be .csv or .dat format
    csv_path = os.path.abspath("../" + csv)
    df = pd.read_csv(csv_path,sep="\s{3,}|\s{3,}|\t+|\s{3,}\t+|\t+\s{3,}",skipinitialspace=True)

    input_cols = ["Ip (MA)","P_tot (MW)","B (T)"]
    real_output_col = ["Te ped height pre-ELM (keV)"]

    test_model = jetdnn.predict.build_and_test_single(csv_path,input_cols,real_output_col)[0]
    output = jetdnn.predict.predict_single(test_model,csv_path,input_cols)

    output_expected = df[real_output_col].values.flatten().tolist()

    assert output == pytest.approx(output_expected,abs=0.7) # 0.7 found to be the absolute error with testing