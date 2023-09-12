import hydroeval as he
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_ts(x,y1,y2,ylabel):
    
    """

    Parameters
    ----------
    x : array of timestamps
        shared time data of the modelled and measured data
    y1 : array of numeric values
        modelled data
    y2 : array of numeric values
        measured data
    ylabel : str
        label of the y-axis

    Returns
    -------
    None.

    """
    
    # GOF
    nse = he.evaluator(he.nse,y1,y2)[0]
    bias = he.evaluator(he.pbias,y1,y2)[0]/100
    
    # Timeseries plot
    plt.plot(x,y1,label='simulation',marker='.',color='grey',alpha=0.5)
    plt.plot(x,y2,label='reference',color='blue')
    plt.legend(loc='upper right')
    plt.ylabel(ylabel)
    plt.text(0.03,0.96, 'NSE = '+str(round(nse,2))+'\nbias = '+str(round(bias,2)),
             verticalalignment='top',transform=plt.gca().transAxes,
             bbox=dict(facecolor='white',edgecolor='lightgrey',linewidth=1))