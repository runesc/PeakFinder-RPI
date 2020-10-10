import statistics as st

def detectPeaks(data_y):
    datanorm=[]
    maximo=max(data_y)
    for k in range(0,len(data_y),10):
        datanorm.append(st.mean(data_y[k:k+9])/maximo)

    der=[]
    for k in range(0,len(datanorm)-1):
        der.append(datanorm[k+1]-datanorm[k])

    peaks=[]
    last_peak=0
    w=40
    whitenoise=st.mean(der[:w])

    if whitenoise<0.001:
        whitenoise=0.001

    for l in range(w,len(der)-w):                                      ######### primer if ##############
        if st.mean(der[l-w:l])<whitenoise*10 and der[l]>whitenoise*50: #Se buscan valores donde el salto entre las derivadas
            if der[l]-der[l-1]>whitenoise*30 and l-last_peak>90:       #sea mayor a 50 veces el ruido, se establece la condicion
                peaks.append(l*10)                                        #de que el promedio del ruido en los ultimos 40 previo al
                last_peak=l                                            #salto sea menor a 10 veces el ruido, de esta forma evitar
    else:                                                               #que se considerar peaks en zonas con mucho ruido.
        pass
    return peaks
