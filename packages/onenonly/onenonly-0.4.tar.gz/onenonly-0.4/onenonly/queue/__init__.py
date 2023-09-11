class Queue:
    def __init__(self,maxSize):
        self.items = []
        self.maxSize = maxSize

    def enqueue(self, item):
        if not self.isFull():
            self.items.append(item)
        else:
            print(f"Queue is full, cannot enqueue: {item}")

    def dequeue(self):
        if not self.isEmpty():
            return self.items.pop(0)
        else:
            print(None)

    def isEmpty(self):
        return len(self.items) == 0
    
    def isFull(self):
        return len(self.items) == self.maxSize

    def size(self):
        print(len(self.items))

    def display(self):
        print(tuple(self.items))

    def indexOf(self,value):
        if value in self.items:
            print(self.items.index(value))
        else:
            print(None)

    def valueAt(self,index):
        if 0 <= index < len(self.items):
            print(self.items[index])
        else:
            print(None)

    def peek(self):
        if not self.is_empty():
            print(self.items[0])
        else:
            print(None)
    
    def isPresent(self, value):
        print(value in self.items)
