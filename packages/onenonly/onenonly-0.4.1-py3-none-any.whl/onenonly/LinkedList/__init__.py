class singlyLinkedList:
    class singlyNode:
        def __init__(self, data):
            self.data = data
            self.next = None

    def __init__(self):
        self.head = None

    def append(self,data):
        newNode = self.singlyNode(data)
        if self.head is None:
            self.head = newNode
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = newNode

    def display(self):
        current = self.head
        while current:
            print(current.data, end=" > ")
            current = current.next
        print(None)

    def length(self):
        current = self.head
        count = 0
        while current:
            count += 1
            current = current.next
        print(count)

    def isPresent(self,target):
        current = self.head
        while current:
            if current.data == target:
                print(True)
                return
            current = current.next
        print(False)

    def indexOf(self,target):
        current = self.head
        count = 0
        while current:
            if current.data == target:
                print(count)
                return
            count += 1
            current = current.next
        print(f"{target} not found in the linked list!")

    def valueAt(self,index:int):
        if index < 0:
            print(None)
            return
        current = self.head
        count = 0
        while current:
            if count == index:
                print(current.data)
                return
            current = current.next
            count += 1
        print(None)

    def remove(self,target):
        if self.head is None:
            return
        if self.head.data == target:
            self.head = self.head.next
            return
        current = self.head
        while current.next:
            if current.next.data == target:
                current.next = current.next.next
                return
            current = current.next

class doublyLinkedList:
    class DoublyNode:
        def __init__(self, data):
            self.data = data
            self.prev = None
            self.next = None

    def __init__(self):
        self.head = None

    def append(self, data):
        newNode = self.DoublyNode(data)
        if self.head is None:
            self.head = newNode
        else:
            current = self.head
            while current.next:
                current = current.next
            newNode.prev = current
            current.next = newNode

    def display(self):
        current = self.head
        while current:
            print(current.data, end=" < > ")
            current = current.next
        print(None)

    def length(self):
        current = self.head
        count = 0
        while current:
            count += 1
            current = current.next
        print(count)

    def isPresent(self,target):
        current = self.head
        while current:
            if current.data == target:
                print(True)
                return
            current = current.next
        print(False)

    def indexOf(self,target):
        current = self.head
        while current:
            if current.data == target:
                print(True)
                return
            current = current.next
        print(False)

    def valueAt(self,index:int):
        if index < 0:
            print(None)
            return
        current = self.head
        current_index = 0
        while current:
            if current_index == index:
                print(current.data)
                return
            current = current.next
            current_index += 1
        print(None)

    def remove(self, target):
        if self.head is None:
            return
        if self.head.data == target:
            self.head = self.head.next
            if self.head:
                self.head.prev = None
            return
        current = self.head
        while current.next:
            if current.next.data == target:
                current.next = current.next.next
                if current.next:
                    current.next.prev = current
                return
            current = current.next
