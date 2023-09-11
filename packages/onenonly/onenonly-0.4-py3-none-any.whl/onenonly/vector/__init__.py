import onenonly.maths as maths
import numpy as np

class Vector:
    def __init__(self,vector):
        for x in vector:
            if not isinstance(x,int|float):
                raise ValueError("Vector must integer or floating values")
        if not isinstance(vector,list):
            vector = list(vector)
        if len(vector) != 3:
            raise ValueError("Vector must have 3 directions")
        self.i = vector[0]
        self.j = vector[1]
        self.k = vector[2]

    def __repr__(self):
        return f"<{self.i} {self.j} {self.k}>"
    
    def __eq__(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        return self.i == other.i and self.j == other.j and self.k == other.k
    
    def __ne__(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        return self.i != other.i and self.j != other.j and self.k != other.k
    
    def toList(self):
        return [self.i,self.j,self.k]

    def get(self,direction):
        if direction == 1:
            return self.i
        elif direction == 2:
            return self.j
        elif direction == 3:
            return self.k
        else:
            raise IndexError("out of range!")

    def assign(self,direction:int,value:int|float):
        if direction == 1:
            self.i = value
        elif direction == 2:
            self.j = value
        elif direction == 3:
            self.k = value
        else:
            raise IndexError("out of range!")
        return Vector((self.i,self.j,self.k))

    def dot(self,other):
        if not isinstance(other,Vector):
            try:
                other = Vector(other)
            except Exception as e:
                return e
        return self.i * other.i + self.j * other.j + self.k * other.k

    def cross(self,other):
        if not isinstance(other,Vector):
            try:
                other = Vector(other)
            except Exception as e:
                return e
        X = self.j * other.k - other.j * self.k
        Y = -(self.i * other.k - other.i * self.k)
        Z = self.i * other.j - self.j * other.i
        return Vector((X,Y,Z))
    
    def magnitude(self):
        return maths.sqrt(self.i * self.i + self.j * self.j + self.k * self.k)
    
    def projection(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        dot_product = self.dot(other)
        other_magnitude_squared = other.magnitude() ** 2
        projection_values = []
        for direction in range(1,4):
            projection_value = (dot_product / other_magnitude_squared) * other.get(direction)
            projection_values.append(projection_value)
        return Vector(projection_values)

    def angle(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        dot = self.dot(other)
        magA = self.magnitude()
        magB = other.magnitude()
        theta = dot / (magA * magB)
        rad = np.arccos(theta)
        return np.degrees(rad)

    def distance(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        di = self.i - other.i
        dj = self.j - other.j
        dk = self.k - other.k
        return maths.sqrt(di ** 2 + dj ** 2 + dk ** 2)
    
    def unitVector(self):
        mag = self.magnitude()
        if mag == 0:
            raise ValueError("can't calculate magnitude for a 0 magnitude vector")
        unitI = self.i / mag
        unitJ = self.j / mag
        unitK = self.k / mag
        return Vector((unitI,unitJ,unitK))

    def orthogonalTo(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        return self.dot(other) == 0
    
    def parallelTo(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        return self.cross(other).magnitude() == 0
    
    def compareWith(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        magA = self.magnitude()
        magB = other.magnitude()
        if magA < magB:
            return -1
        elif magA == magB:
            return 0
        else:
            return 1
    
    def scalarProjection(self,other):
        if not isinstance(other,Vector):
            other = Vector(other)
        dot_product = self.dot(other)
        onto_vector_magnitude_squared = other.magnitude() ** 2
        scalar_projection = dot_product / onto_vector_magnitude_squared
        return scalar_projection

    def add(self,other):
        if isinstance(other,int|float):
            return Vector((self.i + other,self.j + other,self.k + other))
        if isinstance(other,Vector):
            return Vector((self.i + other.i,self.j + other.j,self.k + other.k))
        raise ValueError("argument should be integer, float or Vector")
    
    def sub(self,other):
        if isinstance(other,int|float):
            return Vector((self.i - other,self.j - other,self.k - other))
        if isinstance(other,Vector):
            return Vector((self.i - other.i,self.j - other.j,self.k - other.k))
        raise ValueError("argument should be integer, float or Vector")
    
    def pow(self,exponent=1.0):
        return Vector((self.i ** exponent,self.j ** exponent,self.k ** exponent))

    def scalarProduct(self,scalar=1.0):
        return Vector((self.i * scalar,self.j * scalar,self.k * scalar))
    
    def div(self,scalar=1.0):
        return Vector((self.i / scalar,self.j / scalar,self.k / scalar))
    
    def floor_div(self,scalar=1.0):
        return Vector((self.i // scalar,self.j // scalar,self.k // scalar))

    def octant(self):
        if self.i == 0 and self.j == 0 and self.k == 0:
            return 0
        if self.i >= 0 and self.j >= 0 and self.k >= 0:
            return 1
        elif self.i < 0 and self.j >= 0 and self.k >= 0:
            return 2
        elif self.i < 0 and self.j < 0 and self.k >= 0:
            return 3
        elif self.i >= 0 and self.j < 0 and self.k >= 0:
            return 4
        elif self.i >= 0 and self.j >= 0 and self.k < 0:
            return 5
        elif self.i < 0 and self.j >= 0 and self.i < 0:
            return 6
        elif self.i < 0 and self.j < 0 and self.k < 0:
            return 7
        elif self.i >= 0 and self.j < 0 and self.k < 0:
            return 8
