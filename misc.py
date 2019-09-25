from functools import reduce
from operator import mul

def f(x):
    total = 0
    for i in range(1,x+1):
        total += reduce(mul, range(i, x+1))
    return total

print(f(1))
print(f(2))
print(f(3))
print(f(4))
print(f(9))