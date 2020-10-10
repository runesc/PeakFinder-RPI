import math
import numpy as np
import statistics as st
from statsmodels.tsa.ar_model import AutoReg

def get_peak(prediccion):
    min=1000
    min_index=0
    index=0
    for entry in prediccion:
        if entry < min:
            min=entry
            min_index=index
        else:
            pass
        index+=1
    max=0
    index=0
    max_index=0
    for entry in prediccion[min_index:]:
        if entry > max:
            max=entry
            max_index=index
        else:
            pass
        index+=1
    peak=min_index+max_index
    return peak

def AutoRegresive(peaks,data):
    maximo=max(data)
    data3s=[]
    for k in range(0,len(data),30):  # 3s por punto
        data3s.append(st.mean(data[k:k+29])/maximo)
    peaks3s = [math.floor(x / 30) for x in peaks]

    predicciones=[]
    training_sets=[]
    i=0
    for peak in peaks[2:-1]:
        training=np.array(data3s[(peaks3s[i])+15:(peaks3s[i+2])+15])
        training_sets.append(training)
        t=len(training)
        pred=np.array([0]*(peaks3s[i+2]))
        mod = AutoReg(training,30)
        results = mod.fit()
        forecast = results.predict(start=t, end=t+90, dynamic=True)
        predicciones.append((peaks3s[i+2]+get_peak(forecast))*30)
        i+=1
    return(predicciones)
