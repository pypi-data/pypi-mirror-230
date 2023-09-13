class Calculator:
    def __init__(self, memory=0):
        self.memory = memory

    def add(self, x):
        self.memory += x
        return self.memory

    def subtract(self, x):
        self.memory -= x
        return self.memory

    def multiply(self, x):
        self.memory *= x
        return self.memory

    def divide(self, x):
        if x == 0:
            print("You can't divide by zero")
            return self.memory
        self.memory /= x
        return self.memory

    def nthroot(self, x):
        if x == 0:
            print("There is no zero root")
            return self.memory
        if x < 0:
            print("You can't take negative number root")
            return self.memory
        if self.memory < 0:
            print("You can't take root from negative number")
            return self.memory
        else:
            self.memory **= (1/x)
            return self.memory

    def reset(self):
        self.memory = 0
        return self.memory


Calculator = Calculator()
