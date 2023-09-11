from onenonly import const
from onenonly import List
import numpy as np

def isMatrix(matrix:list):
    if not isinstance(matrix,list):
        return const.false
    num_columns = len(matrix[0]) if matrix else const.NULL
    for row in matrix:
        if not isinstance(row, list) or len(row) != num_columns:
            return const.false
    return const.true

def toMatrix(array:list,dim:tuple):
    array = List.flatten(array)
    rows,cols = dim
    if rows*cols != len(array):
        raise ValueError("can't rehape the matrix to the specified dimensions!")
    matrix = []
    index = 0
    for _ in range(rows):
        row = []
        for _ in range(cols):
            row.append(array[index])
            index += 1
        matrix.append(row)
    return np.array(matrix)

def df2matrix(dataframe):
    matrix = []
    columns = list(dataframe.columns)
    for index,row in dataframe.iterrows():
        matrix_row = []
        for column in columns:
            matrix_row.append(row[column])
        matrix.append(matrix_row)
    return np.array(matrix)

def reshape(matrix:list,dim:tuple):
    if not isMatrix(matrix):
        raise ValueError("Error: input should be a matrix")
    rows,cols = dim
    if len(matrix)*len(matrix[0]) != rows*cols:
        raise ValueError("can't reshape the matrix to the specified dimensions!")
    newMatrix = []
    newRow = []
    count = 0
    for row in matrix:
        for value in row:
            newRow.append(value)
            count += 1
            if count == cols:
                newMatrix.append(newRow)
                newRow = []
                count = 0
    return np.array(newMatrix)
    
def isSquare(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    if len(matrix) != len(matrix[0]):
        return const.false
    return const.true
    
def dim(matrix:list):
    if not isMatrix(matrix):
            raise ValueError("Error: given nested list isn't in the form of matrix")
    return len(matrix)

def shape(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    return (len(matrix),len(matrix[0]))
    
def size(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    return len(matrix)*len(matrix[0])
    
def info(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    is_square = False
    if isSquare(matrix):
        is_square = True
    return (dim(matrix),shape(matrix),size(matrix),is_square)
    
def zeros(shape:tuple):
    rows,cols = shape
    return np.array([[0]*cols for _ in range(rows)])

def ones(shape:tuple):
    rows,cols = shape
    return np.array([[1]*cols for _ in range(rows)])
    
def dummy(shape:tuple,value:int|float = const.nan):
    rows,cols = shape
    return np.array([[value]*cols for _ in range(rows)])

def add(*matrices:list):
    for matrix in matrices:
        if not isMatrix(matrix):
            raise ValueError("Error: given nested list isn't in the form of matrix")
    if len(set(len(matrix) for matrix in matrices)) != 1 or len(set(len(row) for matrix in matrices for row in matrix)) != 1:
        raise ValueError("All matrices must have the same dimensions for addition.")
    result = [[sum(matrix[i][j] for matrix in matrices) for j in range(len(matrices[0][i]))] for i in range(len(matrices[0]))]
    return np.array(result)
    
def scalarAdd(matrix:list,scalar:int|float=0):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    result = [[matrix[i][j]+scalar for j in range(len(matrix[i]))] for i in range(len(matrix))]
    return np.array(result)
    
def sub(*matrices:list):
    for matrix in matrices:
        if not isMatrix(matrix):
            raise ValueError("Error: given nested list isn't in the form of matrix")
    if len(set(len(matrix) for matrix in matrices)) != 1 or len(set(len(row) for matrix in matrices for row in matrix)) != 1:
        raise ValueError("All matrices must have the same dimensions for subtraction.")
    result = [[matrices[0][i][j]-sum(matrix[i][j] for matrix in matrices[1:]) for j in range(len(matrices[0][i]))] for i in range(len(matrices[0]))]
    return np.array(result)

def scalarSub(matrix:list,scalar:int|float=0):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    result = [[matrix[i][j]-scalar for j in range(len(matrix[i]))] for i in range(len(matrix))]
    return np.array(result)

def product(*matrices:list):
    result = matrices[0]
    for matrix in matrices[1:]:
        rowsResult = len(result)
        colsResult = len(result[0])
        rowsMatrix = len(matrix)
        colsMatrix = len(matrix[0])
        if colsResult != rowsMatrix:
            raise ValueError("Error: matrix dimensions are not compatible for multiplication!")
        newResult = [[0] * colsMatrix for _ in range(rowsResult)]
        for i in range(rowsResult):
            for j in range(colsMatrix):
                sum = 0
                for k in range(colsResult):
                    sum += result[i][k] * matrix[k][j]
                newResult[i][j] = sum
        result = newResult
    return np.array(result)

def scalarProduct(matrix:list,scalar:int|float=1):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix!")
    result = [[matrix[i][j] * scalar for j in range(len(matrix[i]))] for i in range(len(matrix))]
    return result
    
def T(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix!")
    result = [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]
    return np.array(result)
    
def subMatrix(matrix:list,shape:tuple):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    row,col = shape
    return np.array([matrix[i][:col] + matrix[i][col+1:] for i in range(len(matrix)) if i != row])
    
def det(matrix:list):
    if len(matrix) == 1:
        return matrix[0][0]
    elif len(matrix) == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    else:
        res = 0
        for col in range(len(matrix)):
            submatrix = [row[:col] + row[col + 1:] for row in matrix[1:]]
            res += matrix[0][col] * det(submatrix) * (-1) ** col
        return res

def cofactor(matrix:list,shape:tuple):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    if not isSquare(matrix):
        raise ValueError("Error: matrix should have same number of rows and cols")
    row,col = shape
    submatrix = [row[:col] + row[col + 1:] for row in (matrix[:row] + matrix[row + 1:])]
    return (-1) ** (row + col) * det(submatrix)

def adjoint(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    if not isSquare(matrix):
        raise ValueError("Error: matrix should have same number of rows and cols")
    cofactors = cofactor(matrix)
    return T(cofactors)

def inv(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: given nested list isn't in the form of matrix")
    if not isSquare(matrix):
        raise ValueError("Error: matrix should have same number of rows and cols")
    x = det(matrix)
    if x == 0:
        return None
    inverse = []
    for i in range(len(matrix)):
        row = []
        for j in range(len(matrix)):
            cofact = cofactor(matrix,(i,j))
            row.append(cofact / x)
        inverse.append(row)
    return np.array(inverse)
    
def trace(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: input should be a matrix")
    if not isSquare(matrix):
        raise ValueError("Error: matrix should have same number of rows and cols")
    traces = 0
    for x in range(len(matrix)):
        traces += matrix[x][x]
    return traces

def identity(row:int):
    id_matrix = []
    for x in range(row):
        new = []
        for y in range(row):
            if x == y:
                new.append(1)
            else:
                new.append(0)
        id_matrix.append(new)
    return np.array(id_matrix)

def eye(N,M=None,k=0,dtype=float):
    if M is None:
        M = N
    iden = np.zeros((N,M),dtype=dtype)
    np.fill_diagonal(iden[max(-k,0):,max(k,0):],1)
    return iden

def diagonalSum(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: input should be a matrix")
    if not isSquare(matrix):
        raise ValueError("Error: matrix should have same number of rows and cols")
    total = 0
    for x in range(len(matrix)):
        total += matrix[x][x]
        total += matrix[len(matrix)-x-1][x]
    if len(matrix)%2 != 0:
        total -= matrix[int(len(matrix)/2)][int(len(matrix)/2)]
    return total
    
def removeCol(matrix:list,column:int):
    if not isMatrix(matrix):
        raise ValueError("Error: input should be a matrix")
    if not isinstance(matrix,list):
        matrix = list(matrix)
    for rows in matrix:
        rows.remove(rows[column])
    return np.array(matrix)
    
def removeRow(matrix:list,row:int):
    if not isMatrix(matrix):
        raise ValueError("Error: input should be a matrix")
    if not isinstance(matrix,list):
        matrix = list(matrix)
    matrix.remove(matrix[row])
    return np.array(matrix)
    
def reciprocal(matrix:list):
    if not isMatrix(matrix):
        raise ValueError("Error: input should be a matrix")
    if not isinstance(matrix,list):
        matrix = list(matrix)
    for rows in matrix:
        for x in range(len(rows)):
            rows[x] = 1/rows[x]
    return np.array(matrix)
