import numpy as np
import pandas as pd

def expand_df(df,sets,names,intensity=True):
    
    """
    Expand a DataFrame by adding additional datasets while aggregating data over the time array of the original DataFrame.
    
    Parameters
    ----------
    df : DataFrame with at least a column "time" (timestamps)
        original data frame
    sets : List of DataFrames each with 2 columns: "time" (timestamps) and "value" (numeric values)
        data frames to be added to the original data frame
    names : List of str
        final column names under which the added data is stored in df
    intensity: bool
        specifies whether data is measured per time. If False, data is adjusted for time intervals.

    Returns
    -------
    df : DataFrame
        combined data sets aggregated over the time array of df
    """
    
    # Set time as index
    time = df.time
    df = df.set_index('time')
    dt0 = np.median(np.diff(df.index)/np.timedelta64(1,'h'))
    
    # Add data to dataframe and interpolate missing time stamps
    for i in range(len(sets)):
        x = sets[i].set_index('time')
        if intensity==False:
            dt = np.median(np.diff(x.index)/np.timedelta64(1,'h'))
            x.value = x.value/dt
        x.columns = [names[i]]
        df = pd.concat([df,x],axis=1).sort_index().interpolate(method='time',limit=12)
        if intensity==False:
            df[names[i]] = df[names[i]]*dt0
    
    # Remove all time stamps not part of the initial data frame
    df = df[~df.index.duplicated(keep='first')]
    df = df[df.index.isin(time)]
    df = df.reset_index()
    
    return df