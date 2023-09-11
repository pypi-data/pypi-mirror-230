class Stack:
    def __init__(self,maxSize):
        self.items = []
        self.maxSize = maxSize

    def push(self,item):
        if len(self.items) < self.maxSize:
            self.items.append(item)
        else:
            raise IndexError("stack is full")

    def pop(self):
        if not self.isEmpty():
            return self.items.pop()
        else:
            raise IndexError("stack is empty")

    def peek(self):
        if not self.isEmpty():
            return self.items[-1]
        else:
            raise IndexError("stack is empty")

    def isEmpty(self):
        return len(self.items) == 0

    def isFull(self):
        return len(self.items) == self.maxSize

    def size(self):
        return len(self.items)

    def display(self):
        return tuple(self.items)
