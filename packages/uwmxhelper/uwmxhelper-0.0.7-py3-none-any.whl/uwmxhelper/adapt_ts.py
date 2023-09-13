import pandas as pd
import numpy as np
import matlab.engine

# Start engine
eng = matlab.engine.start_matlab()

def adapt_ts(time,value,startdate):
    
    """
    
    Parameters
    ----------
    time : array of timestamps
        time data
    value : array of numeric values
        measurement data (usually rain data)
    startdate : timestamp
        date of first measurement

    Returns
    -------
    ts_simulink : dict
        timeseries in the required structure for simulink blocks (usually "RainReadFromWorkspace" )

    """
    
    # Create relative time
    time_rel = (time-pd.to_datetime(startdate))/np.timedelta64(1,'s')
    
    # Create simulink compatible data
    a = eng.transpose(matlab.double(list(time_rel)))
    b = eng.transpose(matlab.double(list(value)))
    ts_simulink = {'time':a,'signals':{'values':b}}
    return ts_simulink