import os
import pandas as pd
import numpy as np
import re
from tkinter import filedialog
from urllib.error import HTTPError
from urllib.request import urlopen

def fetch_data(file:str,ext:str="csv",lim:str=","):
    try:
        src = f"https://raw.githubusercontent.com/Sahil-Rajwar-2004/Datasets/master/{file}.{ext}"
        return pd.read_csv(src,sep = lim)
    except HTTPError as error:
        return f"{error} | {file}.{ext} not found! | try changing the extension .{ext} or filename."
    
def fetch_data_dir(directory:str=os.getcwd(),lim:str=","):
    try:
        PATH = filedialog.askopenfilename(initialdir = directory,filetypes = [("CSV","*.csv"),("DATA","*.data"),("EXCEL",".xlsx"),("JSON","*.json"),("XML",".xml")])
        if not PATH:
            return None
        if PATH.endswith(".csv") or PATH.endswith(".data"):
            return pd.read_csv(PATH,sep=lim)
        elif PATH.endswith(".json"):
            return pd.read_json(PATH)
        elif PATH.endswith(".xlsx"):
            return pd.read_excel(PATH)
        elif PATH.endswith(".xml"):
            return pd.read_xml(PATH)
    except FileNotFoundError as fileNotFoundError:
        return fileNotFoundError

def fetch_remote_dataset_lists():
    url = "https://github.com/Sahil-Rajwar-2004/Datasets"
    with urlopen(url) as resp:
        html = resp.read()
    pattern = r"/Sahil-Rajwar-2004/Datasets/blob/master/([\w.-]*)"
    datasets = re.findall(pattern,html.decode())
    return np.array([dataset for dataset in datasets if not dataset.endswith(".md")])

def get_data_files_list(directory = os.getcwd()):
    datasetFiles = []
    for root,dirs,files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.csv','.json','.xlsx','.data')):
                datasetFiles.append(file)
    return np.array(datasetFiles)
