import numpy as np
import pandas as pd

def convert_UWOflow(df):
    
    """
    Parameters
    ----------
    df : DataFrame containting 12 columns: timestamp;average_velocity;battery_charge;battery_voltage;device_temperature;distance;flow_rate;nos;pmr;rssi;surface_velocity;water_level
        Raw UWO monitoring data (inflow from Russikon/Rumlikon to Fehraltorf)

    Returns
    -------
    df : DataFrame with 2 columns: "time" (timestamps) and "value" (numeric values)
        Formatted flow rate data

    """
    
    df.drop(df.columns[[1,2,3,4,5,7,8,9,10,11]],axis=1,inplace=True)
    df.replace('-',np.nan,inplace=True)
    df.dropna(inplace=True)
    df.columns = ['time','value']
    df.time = pd.to_datetime(df.time,format='%Y-%m-%d %H:%M:%S')
    df.value = df.value.astype('float')
    df.reset_index(inplace=True,drop=True)
    
    return df