import numpy as np
import pandas as pd

def convert_UWOrYoung(df):
    
    """
    Parameters
    ----------
    df : DataFrame containting 8 columns timestamp;battery_voltage;frame_counter;rainfall_cumsum;rainfall_intensity;rssi;sf;snr
        Raw UWO rainfall data (rain gauge RM-Young Fehraltorf)

    Returns
    -------
    df : DataFrame with 2 columns: "time" (timestamps) and "value" (numeric values)
        Formatted flow rate data

    """
    
    df.drop(df.columns[[1,2,3,5,6,7]],axis=1,inplace=True)
    df.replace('-',np.nan,inplace=True)
    df.dropna(inplace=True)
    df.columns = ['time','value']
    df.time = pd.to_datetime(df.time,format='%Y-%m-%d %H:%M:%S')
    df.value = df.value.astype('float')
    df.reset_index(inplace=True,drop=True)
    
    return df