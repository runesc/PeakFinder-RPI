import math
def compute_average(peaks):
    diferencias=[]
    i=1
    for entry in range(len(peaks)-1):
        diferencias.append(abs(peaks[i-1]-peaks[i]))
        i+=1
    return (sum(diferencias)/len(diferencias))/10

def compute_std(peaks):
    diferencias=[]
    i=1
    for entry in range(len(peaks)-1):
        diferencias.append(abs(peaks[i-1]-peaks[i]))
        i+=1
    mean=sum(diferencias)/len(diferencias)
    var=sum(pow(x-mean,2) for x in diferencias)/(len(diferencias)-1)
    return math.sqrt(var)/10

def compute_accuracy(peaks,pred):
    if len(pred)==len(peaks):
        good_pred=0
        for index in range(len(pred)):
            dif=pred[index]-peaks[index]
            if dif < 300 and dif > -600:
                good_pred+=1
            else:
                pass
        return (good_pred/len(peaks))*100

    else:
        return "Err"
def compute_errormedio(peaks,pred):
    if len(pred)==len(peaks):
        error=0
        for index in range(len(pred)):
            dif=(pred[index]-peaks[index])/10
            error+=abs(dif)
        merror=error/len(peaks)
        return merror
    else:
        return "Err"
