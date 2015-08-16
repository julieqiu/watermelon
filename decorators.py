def sum(a, b):
    return a + b

tom = sum


def hello(msg):
    hello = msg
    def speak(animal):
        print animal, "says", hello
    return speak


def hello():
    print 'Julie'

def make_twice_version(func):
    def new_function():
        func()
        func()
    return new_function

f = make_twice_version(hello)
print f

def validateFirstArgsIsLessThan(x):
    def decorator(func):
        def new_function(a,b):
            assert a < x
            return func(a,b)
        return new_function
    return decorator

@validateFirstArgIsLessThan(5)
def sum(a,b):
    return a+b
