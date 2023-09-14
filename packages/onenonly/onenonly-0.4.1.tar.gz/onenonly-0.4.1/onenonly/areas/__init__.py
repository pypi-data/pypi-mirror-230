import onenonly.maths as maths
import onenonly.const as const

def square(side:int|float):
    return side*side

def rectangle(length:int|float,breadth:int|float):
    return length*breadth

def equiTriangle(length:int|float):
    return length**2*maths.sqrt(3)/4

def isoTriangle(a:int|float,b:int|float):
    return (b*maths.sqrt(a**2-b**2/4))/2

def circle(radius:int|float):
    return const.PI*radius**2

def semiCircle(radius:int|float):
    return const.PI*radius**2/2

def quarterCircle(radius:int|float):
    return const.PI*radius**2/4

def sector(radius:int|float,angle:int|float,unit:str="deg"):
    if unit == "rad":
        angle = maths.rad2deg(angle)
        return const.PI*radius**2*angle/360
    elif unit == "deg":
        return const.PI*radius**2*angle/360
    else:
        raise ValueError(f"Invalid unit: deg or rad were expected but got {unit}!")
