import pandas as pd

def write_swmm_ts(data,filename):
    """
    Write time series data to a SWMM (Storm Water Management Model) compatible file.

    Parameters:
    - data (DataFrame): A DataFrame containing time series data with columns 'time' and 'value'.
                       'time' should be in datetime format, and 'value' contains the data values.
    - filename (str): The name of the file to which the SWMM-compatible time series data will be written.

    The function converts the provided DataFrame into a SWMM-compatible format and writes it to a file.
    The SWMM format includes date, daytime, and value columns separated by tabs ('\t').

    Returns:
    None. The function writes the data to the specified file but does not return any values.
    """
    
    # Modify dataframe
    df = pd.DataFrame()
    df['date'] = data.time.dt.strftime('%m/%d/%Y')
    df['daytime'] = data.time.dt.strftime('%H:%M')
    df['value'] = data.value
    
    # Write out dataframe
    df.to_csv(filename,header=None,index=None,sep='\t')