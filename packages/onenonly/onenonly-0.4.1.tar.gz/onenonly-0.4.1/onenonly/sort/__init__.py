def bubbleSort(array:list,reverse=False):
    for i in range(len(array)):
        for j in range(0,len(array)-i-1):
            if not reverse:
                if array[j] > array[j+1]:
                    array[j],array[j+1] = array[j+1],array[j]
            if reverse:
                if array[j] < array[j+1]:
                    array[j],array[j+1] = array[j+1],array[j]
    return array

def quickSort(array:list):
    if len(array) <= 1:
        return array
    pivot = array[len(array)//2]
    left = [x for x in array if x < pivot]
    middle = [x for x in array if x == pivot]
    right = [x for x in array if x > pivot]
    return quickSort(left)+middle+quickSort(right)

def insertionSort(array:list):
    for x in range(len(array)):
        y = x
        while y > 0 and array[y] < array[y-1]:
            array[y],array[y-1] = array[y-1],array[y]
            y -= 1
    return array

def selectionSort(array:list):
    for x in range(len(array)):
        minIndex = x
        for y in range(x+1,len(array)):
            if array[y] < array[minIndex]:
                minIndex = y
        array[x],array[minIndex] = array[minIndex],array[y]
    return array

def descendingSort(array):
    for i in range(len(array)):
        for j in range(i+1,len(array)):
            if array[j] > array[i]:
                array[i],array[j] = array[j],array[i]
    return array
