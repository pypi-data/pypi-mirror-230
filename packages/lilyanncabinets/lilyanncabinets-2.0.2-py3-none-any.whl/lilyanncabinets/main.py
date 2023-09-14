import math

def s_equation(x): #slow decrease equation
    e = math.e
    return 1-math.pow(e, -0.005 * x)
def f_equation(x):
    e = math.e
    return 0.04 * math.pow(e, 0.01 * x) #fast decrease equation