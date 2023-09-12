import numpy as np
import pandas as pd

def convert_UWOrPluvio(df):
    
    """
    Parameters
    ----------
    df : DataFrame containting 5 columns: timestamp;battery_voltage;bucket_content;error_message;rainfall_intensity
        Raw UWO rainfall data (rain gauge Ott Pluvio Fehraltorf)

    Returns
    -------
    df : DataFrame with 2 columns: "time" (timestamps) and "value" (numeric values)
        Formatted rainfall intensity data

    """
    
    df.drop(df.columns[[1,2,3]],axis=1,inplace=True)
    df.replace('-',np.nan,inplace=True)
    df.dropna(inplace=True)
    df.columns = ['time','value']
    df.time = pd.to_datetime(df.time,format='%Y-%m-%d %H:%M:%S')
    df.value = df.value.astype('float')
    df.reset_index(inplace=True,drop=True)
    
    return df