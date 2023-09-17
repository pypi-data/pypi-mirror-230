# JET DNN

JETDNN: a Python framework for building analytic models relating plasma pedestal heights with multiple engineering parameters, using Deep Neural Networks (DNNs). JETDNN functions cover 3 main areas: data inspection, model building, and visualisation.
Created by S. Frankel, J. Simpson and E. Solano.

[![DOI](https://zenodo.org/badge/682657741.svg)](https://zenodo.org/badge/latestdoi/682657741) [![Documentation Status](https://readthedocs.org/projects/jetdnn/badge/?version=latest)](https://jetdnn.readthedocs.io/en/latest/?badge=latest)

Installation
------------------

To use JETDNN, install it in the console using pip:
    
`$ pip install jetdnn`

or

`$ pip install JETDNN`

Requirements
------------------

The packages required to run JETDNN can be found on GitHub here: https://github.com/quasoph/jetdnn/blob/main/requirements.txt.

Functions
------------------

JETDNN functions cover three main areas: data inspection, pedestal prediction, and visualisation. Detailed documentation can be found at https://jetdnn.readthedocs.io/en/latest/.

An example workflow can look like:

1. Inspect data with `jetdnn.interpret.plot_params()` to find engineering parameters strongly correlated to pedestal heights.

2. Train and test a DNN to find a model relating these parameters with pedestal height, using `jetdnn.predict.build_and_test_single()`.

3. Predict pedestal heights using this model from any dataset with `jetdnn.predict.predict_single()`.

4. Visualise model as an analytic equation with functions from `jetdnn.visualise`.
