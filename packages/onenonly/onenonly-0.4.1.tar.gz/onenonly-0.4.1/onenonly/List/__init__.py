def element_wise_operation(*lists:list,operation):
    listLengths = set(len(arg) for arg in lists)
    if not all(isinstance(arg, list) for arg in lists) or len(listLengths) != 1:
        raise ValueError("All arguments must be lists with the same length for element-wise operations.")
    result = [lists[0][i] for i in range(len(lists[0]))]
    for i in range(len(result)):
        for arg in lists[1:]:
            result[i] = operation(result[i],arg[i])
    return result

def dotProduct(*lists:list):
    arrayLength = len(lists[0])
    result = [1]*arrayLength
    for array in lists:
        if len(array) != arrayLength:
            raise ValueError("All arrays must have the same length")
        for i in range(arrayLength):
            result[i] *= array[i]
    return sum(result)

def product(*lists:list):
    return element_wise_operation(*lists,operation=lambda x,y: x*y)

def scalarProduct(lst:list,scalar:int|float=1):
    if not isinstance(lst, list):
        raise ValueError("The first argument must be a list.")
    return [val*scalar for val in lst]

def add(*lists:list):
    return element_wise_operation(*lists,operation=lambda x,y: x+y)

def scalarAdd(lst:list,scalar:int|float=0):
    if not isinstance(lst,list):
        raise ValueError("The first argument must be a list.")
    return [val+scalar for val in lst]

def sub(*lists:list):
    return element_wise_operation(*lists,operation=lambda x,y: x-y)

def scalarSub(lst:list,scalar:int|float=0):
    if not isinstance(lst,list):
        raise ValueError("The first argument must be a list.")
    return [val-scalar for val in lst]

def div(*lists:list):
    return element_wise_operation(*lists,operation=lambda x,y: x/y)

def scalarDiv(lst:list,scalar:int|float=1):
    if not isinstance(lst,list):
        raise ValueError("The first argument must be a list.")
    return [val/scalar for val in lst]

def floorDiv(*lists:list):
    return element_wise_operation(*lists,operation=lambda x,y: x//y)

def scalarFloorDiv(lst:list,scalar:int|float=1):
    if not isinstance(lst,list):
        raise ValueError("The first argument must be a list.")
    return [val//scalar for val in lst]

def modulo(*lists:list):
    return element_wise_operation(*lists,operation=lambda x,y: x%y)

def scalarModulo(lst:list,scalar:int|float=1):
    if not isinstance(lst, list):
        raise ValueError("The first argument must be a list.")
    return [val%scalar for val in lst]

def pow(lst:list,scalar:int|float=1):
    if not isinstance(lst, list):
        raise ValueError("The first argument must be a list.")
    return [val**scalar for val in lst]

def flatten(lst:list):
    flattenedList = []
    for item in lst:
        if isinstance(item,list):
            flattenedList.extend(flatten(item))
        else:
            flattenedList.append(item)
    return flattenedList
