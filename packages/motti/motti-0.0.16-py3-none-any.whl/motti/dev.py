import motti
import random

def foo():
    r = random.randint(0,9)
    return "Hello world" + str(r)

def foo2():
    res = motti.foo()
    r2 = random.randint(0,9)
    return res + str(r2)

