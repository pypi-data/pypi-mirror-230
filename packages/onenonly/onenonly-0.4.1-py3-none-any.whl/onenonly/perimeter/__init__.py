import onenonly.const as const

def square(side:int|float):
    return 4*side

def rectangle(length:int|float,breadth:int|float):
    return 2*(length+breadth)

def triangle(a:int|float,b:int|float,c:int|float):
    return a+b+c

def circumference(radius:int|float):
    return 2*const.PI*radius

def semiCircumference(radius:int|float):
    return const.PI*radius

def quarterCircumference(radius:int|float):
    return const.PI*radius/2

def sector(angle:int|float,radius:int|float):
    return angle/360*circumference(radius)+2*radius
