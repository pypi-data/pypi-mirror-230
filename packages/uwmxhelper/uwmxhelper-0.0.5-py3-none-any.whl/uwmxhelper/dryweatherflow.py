import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def dryweatherflow(time,rain,flow,lag,quantiles,ylabel):
    
    """

    Parameters
    ----------
    time : array of timestamps
        shared time data of rain and flow data
    rain : array of numeric values
        rain measurements
    flow : array of numeric values
        flow measurements
    lag : int
        days after a rain event where dry weather flow is not yet reestablished
    quantiles : array of 2 numeric values
        lower and higher quantile for statistical visualisation 
    ylabel : str
        label of the y-axis

    Returns
    -------
    df : pandas dataframe
        average dry weather flow at a given daytime

    """
    
    # Create dataframe
    data = pd.DataFrame({'time':time,'flow':flow,'rain':rain})
    
    # Expand data with aggregation attributes
    data['dayid'] = (data.time.dt.year-min(data.time.dt.year))*1000 + data.time.dt.day_of_year
    data['daytime'] = data.time.dt.hour + data.time.dt.minute/60

    # Expand data with dry weather day indicator
    ridx = np.unique(data.dayid[data.rain>0])
    for i in range(lag):
        ridx = np.append(ridx,ridx+i+1)
    data['dw'] = np.where(data.dayid.isin(ridx),0,1)

    # Create daily cycle dataframe
    dataDC = pd.DataFrame(columns=['daytime','m','l','h','mh','lh','hh'])
    
    # Define time window for rolling mean calculation (1 hour)
    dt = pd.Timedelta(data.time.values[1]-data.time.values[0])/np.timedelta64(1,'s')
    agg = int(3600/dt+1)
    
    # Fill dataframe with mean, upper and lower quantile at every daytime timestamp
    dataDC.daytime = data[data.dw==1].groupby(['daytime']).mean(numeric_only=True).index
    dataDC.m = data[data.dw==1].groupby(['daytime']).mean(numeric_only=True).flow.values
    dataDC.l = data[data.dw==1].groupby(['daytime']).quantile(quantiles[0],numeric_only=True).flow.values
    dataDC.h = data[data.dw==1].groupby(['daytime']).quantile(quantiles[1],numeric_only=True).flow.values
    
    # Expand dataframe for rolling mean calculations
    dataDC = pd.concat([dataDC,dataDC,dataDC]).reset_index(drop=True)
    
    # Define index of the full hours
    hours = range(24)
    idx = np.where(dataDC.daytime.isin(hours),1,np.nan)
    
    # Fill dataframe with rolling means at the full hours
    dataDC.mh = dataDC.rolling(agg,center=True).mean(numeric_only=True).m.values*idx
    dataDC.lh = dataDC.rolling(agg,center=True).mean(numeric_only=True).l.values*idx
    dataDC.hh = dataDC.rolling(agg,center=True).mean(numeric_only=True).h.values*idx
    
    # Truncate dataframe back to a single day
    dataDC = dataDC.truncate(len(dataDC)/3,len(dataDC)/3*2-1).reset_index(drop=True)
    
    # Plot results
    plt.vlines(x=dataDC.daytime,ymin=dataDC.lh,ymax=dataDC.hh,color='black',alpha=0.3,linewidth=5)
    plt.plot(dataDC.daytime,dataDC.m,color='blue',alpha=0.5)
    plt.plot(dataDC.daytime,dataDC.mh,'o',color='blue')
    plt.xlabel('Daytime [h]')
    plt.ylabel(ylabel)
    
    # Return hourly mean value
    df = dataDC.drop(labels=['m','l','h','lh','hh'],axis=1)
    df.rename(columns={'mh':'mean'},inplace=True)
    df.dropna(inplace=True)
    
    return df