import tensorflow
from tensorflow import keras
import predict
from keras.utils import plot_model
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from sympy import *

# get equation

import numpy as np
import tensorflow as tf

def get_equation(model,test_data,input_cols,output_col):
    """
    get_equation

    Produce an analytic equation from a trained DNN model, using forward propagation with numerical methods.

    Args:
        model (Tensorflow Model): trained DNN from build_and_test_single.
        input_cols (list): list of input columns as strings (should be the same as those used to test the DNN).

    Returns:
        string: short_eqn, an analytic equation representing the DNN model.
        list: x, the predicted values (should align with those returned by model.predict).
    """

    def activation_relu(input):
        
        output = np.maximum(0,input)

        return output
        
    node_equations = []

    #data = pd.read_csv(filename,sep="\s{3,}|\s{3,}|\t+|\s{3,}\t+|\t+\s{3,}",skipinitialspace=True)

    x = test_data[input_cols]
    layer_nodes = [len(input_cols),128,128,1]
    
    for n in range(0,len(model.layers)): # for each layer
        layer = model.layers[n]
        weights = layer.get_weights() # get list of weights for one layer e.g. W[0][1],W[0][2]
        b = weights[1] # define bias
        w = weights[0] # define weights
        nodes = []

        if n != 0: # try removing this next time you're testing

            for j in range(0,layer_nodes[n]): # for each node (e.g. for each weight in w0 e.g. w01, w02, w03 etc)
                node = 0
                node_eqn = ""

                for i in range(0,len(input_cols)): # for each input, add weights and inputs to node

                    if n == 1: # why 1 and not 0??
                        x_eqn = "x" + str(i)
                    
                    if isinstance(x,pd.DataFrame):
                        col = np.array(x.iloc[:,i]) # gets ith column, converts to numpy array
                    else:
                        col = x[i]

                    # BUILD NODE
                    
                    node += (col * float(w[i,j])) # gives the jth value in i

                    # BUILD MAIN NODE EQUATION BEFORE ADDING BIAS
                    
                    if x_eqn != "x" + str(i): # if not the first layer: IGNORE FOR FIRST PASS OF n!
                        if node_equations[i] == node_equations[-1]: # if last iteration
                            x_eqn = node_equations[i]
                            node_eqn += "(" + str(x_eqn) + ")" + "*" + str(w[i,j]) # finish off equation
                        else:
                            x_eqn = node_equations[i] # multiply appropriate equation with weight
                            node_eqn += "(" + str(x_eqn) + ")" + "*" + str(w[i,j]) + " + "

                    else:
                        if i == len(input_cols): # if the final iteration, finishes off expression
                            node_eqn += str(x_eqn) + "*" + str(w[i,j])
                        else:
                            node_eqn += str(x_eqn) + "*" + str(w[i,j]) + " + "

                    # BUILDS NODES AND NODE EQUATIONS (WITHOUT BIASES) BY END OF ALL i ITERATIONS
                
                node += b[j] # node now contains weights and bias
                node_eqn += str(b[j])
                
                if activation_relu(node) is not 0: # if +ive node value

                    nodes.append(activation_relu(node)) # add node to node list for that layer
                    node_equations.append(node_eqn) # add node equation to list for that layer


            x = nodes # node values become new inputs
            x_eqn = node_equations # list of node equations for that layer
                
    

    # now out of all loops
    
    final_eqn = node_equations[-1] # this should be the final equation

    smpl = simplify(final_eqn)

    print(final_eqn)
    print(smpl)
    print(x)

    #x = list(x.flatten()) # converts x to 1d list (not needed, x already list)

    return smpl, final_eqn, x


# VISUALISE MODELS

def display_model(model):

    """
    display_model

    Display a summary and save a Keras plot of a Deep Neural Network model.

    Args:
        model (Tensorflow Model): Deep Neural Network model build with build_and_test_single.
    
    Returns:
        None
    """
    print(model.summary())
    plot_model(model, to_file='dnn_model_plot.png', show_shapes=True, show_layer_names=True)
    return

# density npm plot
