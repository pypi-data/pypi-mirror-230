import hydroeval as he
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_ts_cum(x,y1,y2,tunit,ylabel):

    """

    Parameters
    ----------
    x : array of timestamps
        shared time data of the modelled and measured data
    y1 : array of numeric values
        modelled data
    y2 : array of numeric values
        measured data
    tunit:  str ('D', 'h', 'm', 's' or None)
        time units of the data
    ylabel : str
        label of the y-axis

    Returns
    -------
    None.

    """ 
    
    # Time step 
    if tunit == None:
        dt = 1
    else:
        dt = pd.Series(0,np.append(np.diff(x)/np.timedelta64(1,tunit)))
    
    # Cummulative values
    Y1 = np.cumsum(y1*dt)
    Y2 = np.cumsum(y2*dt)
    
    # Total volume [%]
    V1 = 100
    V2 = int(np.nanmax(Y2)/np.nanmax(Y1)*100)
    
    # Cumulative plot
    plt.plot(x,Y1,label='simulation',marker='.',color='grey',alpha=0.5)
    plt.plot(x,Y2,label='reference',color='blue')
    plt.legend(loc='upper right')
    plt.ylabel(ylabel)
    plt.text(0.03,0.96, '$V_{sim}$ = '+str(V1)+' %'+'\n$V_{ref}$ = '+str(V2)+' %',
             verticalalignment='top',transform=plt.gca().transAxes,
             bbox=dict(facecolor='white',edgecolor='lightgrey',linewidth=1))