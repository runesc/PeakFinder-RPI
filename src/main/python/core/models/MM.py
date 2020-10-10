import statistics as st
import numpy as np
import math

def mediaMovil(peaks):
    predicciones=[]
    i=0
    for peak in peaks[2:-1]:
        pred=np.array([0]*(peaks[i+2]))
        d1=peaks[i+1]-peaks[i]
        d2=peaks[i+2]-peaks[i+1]
        new_peak=math.floor((d1*0.5+d2*0.5))
        pred_peak=peaks[i+2]+new_peak
        predicciones.append(pred_peak)
        i+=1
    return predicciones
