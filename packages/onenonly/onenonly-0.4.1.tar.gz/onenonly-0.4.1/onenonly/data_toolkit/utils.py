import numpy as np
import pandas as pd

def split(x,y,test_size=0.2,seed=None):
    if seed is not None:
        np.random.seed(seed)
    indices = np.arange(len(x))
    np.random.shuffle(indices)
    test_samples = int(len(x)*test_size)
    train_indices = indices[test_samples:]
    test_indices = indices[:test_samples]
    xtrain = x.iloc[train_indices]
    ytrain = y.iloc[train_indices]
    xtest = x.iloc[test_indices]
    ytest = y.iloc[test_indices]
    return xtrain,ytrain,xtest,ytest

def df2matrix(dataframe):
    num_rows = len(dataframe)
    num_cols = len(dataframe.columns)
    numpy_array = np.empty((num_rows, num_cols), dtype=dataframe.values.dtype)
    for i, column in enumerate(dataframe.columns):
        numpy_array[:,i] = dataframe[column].values
    return numpy_array

def drop(dataframe,index,via="row"):
    if not isinstance(dataframe,(np.matrix,np.ndarray,list)):
        dataframe = np.matrix(dataframe)
    if via == "row":
        new_data = np.delete(dataframe,index,axis=0)
    elif via == "column":
        new_data = np.delete(dataframe,index,axis=1)
    else:
        return "Invalid 'via' parameter"
    return new_data

def dropExact(dataframe,loc:tuple):
    if not isinstance(dataframe,(np.matrix,np.ndarray,list)):
        dataframe = np.matrix(dataframe)
    row,col = loc
    dataframe[row][col] = float("nan")
    return dataframe

def describe(dataframe):
    data = np.array(dataframe)
    mean_values = np.mean(data,axis=0)
    median_values = np.median(data,axis=0)
    std_dev = np.std(data,axis=0)
    min_values = np.min(data,axis=0)
    max_values = np.max(data,axis=0)
    first_quartiles = np.percentile(data,25,axis=0)
    second_quartiles = np.percentile(data,50,axis=0)
    third_quartiles = np.percentile(data,75,axis=0)
    data_range = max_values-min_values
    statistics_dict = {
        "Mean": mean_values,
        "Median": median_values,
        "StandardDeviation": std_dev,
        "Minimum": min_values,
        "Maximum": max_values,
        "First Quartile": first_quartiles,
        "Second Quartile": second_quartiles,
        "Third Quartile": third_quartiles,
        "Range": data_range
    }
    return pd.DataFrame(statistics_dict)

def isnan(dataframe):
    if not isinstance(dataframe,(np.matrix,np.ndarray)):
        dataframe = np.matrix(dataframe)
    for row in dataframe:
        for value in row:
            if value != value:
                return True
    return False
    
