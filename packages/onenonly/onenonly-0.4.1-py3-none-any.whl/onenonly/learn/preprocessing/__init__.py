import numpy as np

def label_encoder(columns):
    unique_labels = np.unique(columns)
    label_mapping = {label: index for index, label in enumerate(unique_labels)}
    encoded_labels = np.array([label_mapping[label] for label in columns])
    return encoded_labels

def minmax_scale(column):
    min_vals = np.min(column,axis=0)
    max_vals = np.max(column,axis=0)
    scaled_data = (column - min_vals) / (max_vals - min_vals)
    return np.array(scaled_data)
