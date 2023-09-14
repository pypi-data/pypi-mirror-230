def linearSearch(array:list,target:int|float):
    for i in range(len(array)):
        if array[i] == target:
            return i
    return -1

def binarySearch(array:list,target:int|float):
    start = 0
    end = len(array)-1
    while start <= end:
        mid = (start+end)//2
        if array[mid] == target:
            return mid
        elif array[mid] < target:
            start = mid + 1
        elif array[mid] > target:
            end = mid - 1
    return -1

def naiveString(text,pattern):
    content = len(text)
    ptn = len(pattern)
    positions = []

    for x in range(content-ptn+1):
        y = 0
        while y < ptn and text[x+y] == pattern[y]:
            y += 1
        if y == ptn:
            positions.append(x)
    return positions
