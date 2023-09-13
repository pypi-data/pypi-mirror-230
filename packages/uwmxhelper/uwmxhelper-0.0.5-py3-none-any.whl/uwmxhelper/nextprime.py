import numpy as np

def nextprime(n):
    """
    target: finds the next prime number
    param n: any number (int)
    return: prime number (int)
    """ 
    p=n+1
    for i in range(2,p):
        if(np.mod(p,i)==0):
            p=p+1
    else:
        return p