import pandas as pd
import numpy as np

def write_swmm_rainfall(data,id,filename):
    
    """
    Parameters
    ----------
    data : DataFrame with 2 columns: "time" (timestamps) and "value" (numeric values)
        Rainfall series
    id : str
        Name of measurement station
    filename : str
        Name of output file including extension

    Returns
    -------
    Writes out SWMM compatible rainfall series
    
    """

    # Modify dataframe
    df = pd.DataFrame()
    df['id'] = np.repeat(id,len(data))
    df['time'] = data.time.dt.strftime('%Y %m %d %H %M')
    df['value'] = data.value
    
    # Write out dataframe (it is not possible to set a space separator)
    df.to_csv(filename,header=None,index=None)
    
    # Replace separator with space
    with open(filename) as f:
        text = f.read().replace(',',' ')
    with open(filename,'w') as f:
        f.write(text)