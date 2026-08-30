import pandas as pd
import numpy as np

def escalar(arr):
    if len(arr)>0:
        return arr*2
    else:
        pass

lista = np.array([2,4,5,6,2])
print(escalar(lista))