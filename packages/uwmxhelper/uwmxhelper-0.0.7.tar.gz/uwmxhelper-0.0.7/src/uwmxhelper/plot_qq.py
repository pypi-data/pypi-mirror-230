import matplotlib.pyplot as plt
import numpy as np

def plot_qq(x,y,xlabel,ylabel):
    
    """
    Generate a Quantile-Quantile (QQ) plot to compare two datasets.

    Parameters
    ----------
    - x (array-like): The first dataset for comparison (measurements, shorter dataset).
    - y (array-like): The second dataset for comparison (modelled, longer dataset).
    - xlabel (str): Label for the x-axis of the QQ plot (describing the array 'x').
    - ylabel (str): Label for the y-axis of the QQ plot (describing the array 'y').

    Generates a QQ plot comparing the quantiles of the two input datasets, 'x' and 'y'.
    The QQ plot visualizes how the quantiles of 'x' compare to those of 'y'.
    
    Returns
    -------
    None.
    """

    # Calculate quantiles of shorter data set
    q1 = np.sort(x)
    q1_lvl = np.arange(len(q1))/len(q1)
    
    # Find quantiles of larger data set using linear interpolation
    q2 = np.sort(y)
    q2_lvl = np.arange(len(q2))/len(q2)
    q2 = np.interp(q1_lvl,q2_lvl,q2)
    
    # QQ-Plot
    ep = max(max(q1),max(q2))
    plt.plot([0,ep],[0,ep],color='blue')
    plt.scatter(q1,q2,color='grey',alpha=0.5,edgecolor='k')
    plt.legend(loc='upper right')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)