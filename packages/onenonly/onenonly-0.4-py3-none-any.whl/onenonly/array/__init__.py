class Array:
    def __init__(self,data):
        self.data = data

    def __repr__(self):
        return repr(self.data)
    
    def __getitem__(self,index):
        return self.data[index]
    
    def __setitem__(self,index,value):
        self.data[index] = value

    def __add__(self,other=0.0):
        if isinstance(other,int|float):
            return [x + other for x in self.data]
        if isinstance(other,list):  
            other = Array(other)
        return [x + y for x,y in zip(self.data,other.data)]

    def __sub__(self,other=0.0):
        if isinstance(other,int|float):
            return [x - other for x in self.data]
        if isinstance(other,list):
            other = Array(other)
        return [x - y for x,y in zip(self.data,other.data)]
    
    def __mul__(self,other=1.0):
        if isinstance(other,int|float):
            return [x * other for x in self.data]
        if isinstance(other,list):
            other = Array(other)
        return [x * y for x,y in zip(self.data,other.data)]
    
    def __truediv__(self,other=1.0):
        if isinstance(other,int|float):
            return [x / other for x in self.data]
        if isinstance(other,list):
            other = Array(other)
        return [x / y for x,y in zip(self.data,other.data)]
    
    def __floordiv__(self,other=1.0):
        if isinstance(other,int|float):
            return [x / other for x in self.data]
        if isinstance(other,list):
            other = Array(other)
        return [x // y for x,y in zip(self.data,other)]
    
    def __pow__(self,scalar=1.0):
        return [x ** scalar for x in self.data]
