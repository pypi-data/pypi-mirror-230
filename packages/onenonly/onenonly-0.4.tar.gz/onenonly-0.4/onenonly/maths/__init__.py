from onenonly import const

def sqrt(number:int|float,precision:float=1e-6):
    if number < 0:
        raise ValueError("Square root is not defined for negative numbers.")
    if number == 0:
        return 0
    x = number
    while abs(x*x-number) > precision:
        x = (x+number/x)/2
    return x

def cbrt(number:int|float,precision:float=1e-6):
    x = number
    while abs(x*x*x-number) > precision:
        x = x-(x*x*x-number)/(3*x*x)
    return x

def factorial(number:int):
    if number == 0:
        return 1
    elif number < 0:
        raise ValueError("number can't be negative!")
    return number*factorial(number-1)

def permutation(n:int,r:int):
    return factorial(n)/factorial(n-r)

def combination(n:int,r:int):
    return factorial(n)/(factorial(r)*factorial(n-r))

def power(base:int|float,exponent:int|float=1):
    return base**exponent

def exp(x:int=1):
    return const.E**x

def length(array:list):
    count = 0
    for _ in array:
        count += 1
    return count

def summation(array:list):
    total = 0
    for x in array:
        total += x
    return total

def product(array:list):
    prod = 1
    for x in array:
        prod *= x
    return prod

def maxVal(array:list):
    val = -const.inf
    for x in array:
        if val < x:
            val = x
    return val

def minVal(array:list):
    val = const.inf
    for x in array:
        if val > x:
            val = x
    return val

def ceil(number:int|float):
    if number == int(number):
        return int(number)
    if number < 0:
        return int(number)-1
    return int(number)+1

def floor(number:int|float):
    if number >= 0:
        return int(number)
    else:
        return int(number)-1

def quadraticRoots(coefs:list):
    if len(coefs) != 3:
        raise ValueError("there should be only 3 coeficients!")
    D = coefs[0]**2-4*coefs[0]*coefs[2]
    if D < 0:
        x1 = -coefs[1] + sqrt(abs(D))
        x2 = -coefs[1] - sqrt(abs(D))
        return [x1,x2]
    x1 = -coefs[1]+sqrt(D)
    x2 = -coefs[1]-sqrt(D)
    return [x1,x2]

def primes(lowerBound:int,upperBound:int):
    primeList = []
    for num in range(max(lowerBound,2),upperBound+1):
        if isPrime(num):
            primeList.append(num)
    return primeList

def isPrime(number:int):
    if number <= 1:
        return const.false
    if number <= 3:
        return const.true
    if number % 2 == 0 or number % 3 == 0:
        return const.false
    i = 5
    while i * i <= number:
        if number % i == 0 or number % (i + 2) == 0:
            return const.false
        i += 6
    return const.true

def findPrimes(array:list):
    return [x for x in array if isPrime(x)]

def isEven(number:int):
    return number%2 == 0

def evens(lowerBound:int,upperBound:int):
    evenList = []
    for num in range(max(lowerBound,2),upperBound+1):
        if isEven(num):
            evenList.append(num)
    return evenList

def findEvens(array:list):
    return [x for x in array if isEven(x)]

def isOdd(number:int):
    return number%2 != 0

def odds(lowerBound:int,upperBound:int):
    oddList = []
    for num in range(max(lowerBound,2),upperBound+1):
        if isOdd(num):
            oddList.append(num)
    return oddList

def findOdds(array:list):
    return [x for x in array if isOdd(x)]

def log(number:int|float):
    if number <= 0:
        raise ValueError("domain error")
    else:
        n = 0
        while number >= 10:
            number /= 10
            n += 1
        if number == 1:
            return n
        else:
            left,right = 0,1
            while number < 1:
                left -= 1
                right -= 1
                number *= 10
            for _ in range(100):
                mid = (left+right)/2
                if 10**mid < number:
                    left = mid
                else:
                    right = mid
            return n+left

def ln(number:int|float):
    if number <= 0:
        raise ValueError("domain error")
    return 2.303*log(number)

def logn(number:int|float,base:int|float=const.E):
    if number <= 0 or base <= 0 or base == 1:
        raise ValueError("domain error")
    return 2.303*log(number)/(2.303*log(base))

def deg2rad(angle:int|float):
    return angle*const.PI/180

def rad2deg(angle:int|float):
    return angle*180/const.PI

def sin(angle:int|float,unit:str="rad"):
    if unit == "deg":
        angle = deg2rad(angle)
    elif unit == "rad":
        if angle > const.PI:
            angle -= 2*const.PI
    else:
        raise ValueError(f"Invalid argument: expected rad or deg but got {unit}")
    sinx = 0
    term = angle
    i = 1
    while abs(term) > 1e-3:
        sinx += term
        term *= -1*angle**2/((2*i)*(2*i+1))
        i += 1
    return round(sinx,4)

def cos(angle:int|float,unit:str="rad"):
    if unit == "deg":
        angle = deg2rad(angle)
    elif unit == "rad":
        if angle > const.PI:
            angle -= 2*const.PI
    else:
        raise ValueError(f"Invalid argument: expected rad or deg but got {unit}")
    cosx = 1
    term = 1
    i = 1
    while abs(term) > 1e-10:
        term *= -1*angle**2/((2*i-1)*2*i)
        cosx += term
        i += 1
    return round(cosx,4)

def tan(angle:int|float,unit:str="rad"):
    if cos(angle,unit) == 0:
        raise ValueError(f"tan({angle}) isn't defined at rad({angle})")
    return sin(angle,unit)/cos(angle,unit)

def cot(angle:int|float,unit:str="str"):
    if sin(angle,unit) == 0:
        raise ValueError(f"cot({angle}) isn't defined at rad({angle})")
    return cos(angle,unit)/sin(angle,unit)

def sec(angle:int|float,unit:str="rad"):
    if cos(angle,unit) == 0:
        raise ValueError(f"sec({angle}) isn't defined at rad({angle})")
    return 1/cos(angle,unit)

def cosec(angle:int|float,unit:str="str"):
    if sin(angle,unit) == 0:
        raise ValueError(f"cosec({angle}) isn't defined at rad({angle})")
    return 1/sin(angle,unit)
