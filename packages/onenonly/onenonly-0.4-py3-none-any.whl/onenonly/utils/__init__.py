import os

def searchFile(filename:str,initialdir:str=os.getcwd(),caseSensitive:bool=False,searchExtension:bool=False):
    matchedFiles = []
    for root, _, files in os.walk(initialdir):
        for file in files:
            if not caseSensitive:
                searchTerm = filename.lower()
                fileLower = file.lower()
            else:
                fileLower = file
            if (searchExtension and fileLower.endswith(searchTerm)) or (searchTerm in fileLower):
                matchedFiles.append(os.path.join(root, file))
    return matchedFiles
