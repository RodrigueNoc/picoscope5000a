class C_test():
    def __init__(self):
        self.x = 0

    def print_x(self):
        def add_x():
            self.x += 1
            self.L = [self.x]
        self.L = []
        add_x()
        return self.L
    
test = C_test()
print(test.print_x())