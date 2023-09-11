import onenonly.maths as maths
import onenonly.sort as sort
import numpy as np

def mean(array:list):
    return maths.summation(array)/maths.length(array)

def median(array:list):
    array.sort()
    n = len(array)
    if n % 2 == 0:
        middle1 = array[n//2-1]
        middle2 = array[n//2]
        median = (middle1+middle2)/2
    else:
        median = array[n//2]
    return median

def mode(array:list):
    counts = {}
    for num in array:
        if num in counts:
            counts[num] += 1
        else:
            counts[num] = 1
    max_count = max(counts.values())
    modes = [num for num, count in counts.items() if count == max_count]
    return modes

def Range(array:list):
    return maths.maxVal(array)-maths.minVal(array)

def variance(array:list,kind:str="sample"):
    if kind == "sample":
        d = len(array)-1
    elif kind == "population":
        d = len(array)
    else:
        raise ValueError(f"invalid input {kind}! input should be whether 'population' or 'sample'")
    return maths.summation((x - mean(array))**2 for x in array)/(d)

def standardDeviation(array:list,kind:str="sample"):
    return maths.sqrt(variance(array,kind))

def mse(actual:list,predicted:list):
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted array aren't equal!")
    errors = [(actual[i]-predicted[i])**2 for i in range(len(actual))]
    return maths.summation(errors)/len(actual)

def rmse(actual:list,predicted:list):
    return maths.sqrt(mse(actual,predicted))

def errors(actual:list,predicted:list):
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted array aren't equal!")
    return [actual[x]-predicted[x] for x in range(len(actual))]

def meanError(actual:list,predicted:list):
    return mean(errors(actual,predicted))

def meanAbsError(actual:list,predicted:list):
    if len(actual) != len(predicted):
        raise ValueError("length of actual and predicted array aren't equal!")
    errors = []
    for x in range(0,len(actual)):
        diff = abs(actual[x]-predicted[x])
        errors.append(diff)
    return sum(errors)/len(actual)

def confusionMatrix(actual:list,predicted:list):
    if len(actual) == len(predicted):
        yTrue = np.array(actual)
        yPred = np.array(predicted)
        nClasses = np.max([yTrue,yPred])+1
        yTrueOnehot = np.eye(nClasses)[yTrue]
        yPredOnehot = np.eye(nClasses)[yPred]
        confMatrix = np.dot(yTrueOnehot.T,yPredOnehot)
        return confMatrix
    elif len(actual) != len(predicted):
        raise ValueError("actual and predicted size should be equal")

def accuracy(yActual:list,yPredicted:list):
    yActual = np.array(yActual)
    yPredicted = np.array(yPredicted)
    correctPredictions = np.sum(np.isclose(yActual,yPredicted))
    totalPredictions = len(yActual)
    accuracy = correctPredictions/totalPredictions
    return accuracy

def correlationCoef(x:list,y:list):
    xMean = sum(x)/len(x)
    yMean = sum(y)/len(x)
    N = sum((xi-xMean)*(yi-yMean) for xi, yi in zip(x, y))
    xD = sum((xi-xMean)**2 for xi in x)
    yD = sum((yi-yMean)**2 for yi in y)
    return N/((xD*yD)**0.5)

def movingAvg(array:list,window:int):
    if window <= 0:
        raise ValueError("Error: window size must be a positive integer!")
    if len(array) < window:
        raise ValueError("Error: array length is smaller than the window size!")
    moving_averages = []
    for i in range(len(array)-window+1):
        window = array[i:i+window]
        average = sum(window)/window
        moving_averages.append(average)
    return moving_averages

def expMovingAvg(array:list,alpha:float):
    if alpha <= 0 or alpha > 1:
        raise ValueError("smoothing factor alpha must be between 0 and 1!")
    ema = [array[0]]
    for i in range(1,len(array)):
        ema.append(round(alpha*array[i]+(1-alpha)*ema[-1],3))
    return ema

def distance(array1:list,array2:list,kind="euclidean"):
    array1 = np.array(array1)
    array2 = np.array(array2)
    if kind == "euclidean":
        return np.sqrt(np.sum((array1 - array2) ** 2)) 
    elif kind == "manhattan":
        return np.sum(np.abs(array1 - array2))
    else:
        return "invalid arguments"

def gradientDescent(x,y,learning_rate=0.01,epochs=1000):
    slope = 0
    intercept = 0
    for _ in range(epochs):
        ypred = slope * x + intercept
        gradient_slope = (-2/len(x)) * np.sum(x * (y - ypred))
        gradient_intercept = (-2/len(x)) * np.sum(y - ypred)
        slope -= learning_rate * gradient_slope
        intercept -= learning_rate * gradient_intercept
    return slope,intercept

def minmax_scale(data:list):
    min_vals = np.min(data,axis=0)
    max_vals = np.max(data,axis=0)
    scaled_data = (data - min_vals) / (max_vals - min_vals)
    return scaled_data

def quartiles(data:list):
    data = sort.bubbleSort(data)
    if len(data) % 2 == 0:
        q1 = median(data[:len(data)//2])
        q2 = median(data)
        q3 = median(data[len(data)//2:])
    else:
        q1 = median(data[:len(data)//2])
        q2 = median(data)
        q3 = median(data[len(data)//2+1:])
    return q1,q2,q3,q3-q1

def outlier(data:list):
    outliers = []
    Q = quartiles(data)
    lowerBound = Q[0] - 1.5 * Q[3]
    upperBound = Q[2] + 1.5 * Q[3]
    for value in data:
        if not lowerBound <= value <= upperBound:
            outliers.append(value)
    return outliers
