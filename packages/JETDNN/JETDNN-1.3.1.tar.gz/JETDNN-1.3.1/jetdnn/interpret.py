import seaborn as sns
import numpy as np
from jetdnn.predict import get_train_test_data # using just .predict gives an error

def plot_params(filename,plot_cols):

    """
    plot_params

    Create a Seaborn pairplot of data, and calculate the correlation coefficients of each subplot to find parameters to input in the DNN.
    Parameters with a strong correlation will be suggested for use in model building.

    Arguments:
        filename (string): name of .dat or .csv file.
        plot_cols (list): list of column names to plot and analyse.

    Returns:
        array: list of columns which are strongly correlated with each other.
    """

    plotting_data = get_train_test_data(filename)
    g = sns.pairplot(plotting_data[plot_cols],diag_kind = "kde") # plots parameters

    labels = []
    print("Correlation significant between:")

    for ax in g.axes:
        for curve in ax.lines:
            
            r = np.corrcoef(curve.get_xdata(),curve.get_ydata()) # find correlation matrix for each subplot

            if (r != 1) and ((r > 0.5) or (r < -0.5)): # if significant correlation
                print(curve.get_label) # list x and y labels
                labels.append(curve.get_label())
            else:
                print() # do nothing

    return labels
