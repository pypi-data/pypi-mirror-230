#Arrays and Lists

#Binary search
def binary_search(arr, x):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = low + (high- low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return -1

#Merge sort
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    elif len(arr) == 2:
        return [min(arr), max(arr)]
    return merge(merge_sort(arr[:len(arr) // 2]), merge_sort(arr[len(arr) // 2:]))

def merge(a1, a2):
    i, j, arr = 0, 0, []
    while True:
        if  i >= len(a1):
            arr += a2[j:]
            break
        elif j >= len(a2):
            arr += a1[i:]
            break
        if a1[i] < a2[j]:
            arr.append(a1[i])
            i += 1
        else:
            arr.append(a2[j])
            j += 1
    return arr

#Quick sort
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    a1 = []
    a2 = []
    for i in arr[1:]:
        if i < arr[0]:
            a1.append(i)
        elif i > arr[0]:
            a2.append(i)
    return quick_sort(a1) + [arr[0]] + quick_sort(a2)

#Sliding window example
def norepeats(arr):
    i, j, m, l = 0, 0, 0, []
    while i < len(arr):
        m = max(m, len(l))
        while arr[i] in l:
            l = l[1:]
        l.append(arr[i])
        i += 1
    m = max(m, len(l))
    return m

#Linked Lists
class ListNode:
    def __init__(self, val, next = None):
        self.val = val
        self.next = next

class linkedList:
    def __init__(self, head):
        self.head = ListNode(head)
        
    def __getitem__(self, k):
        i = -1
        cur = self.head
        while cur:
            if i == k:
                return cur.val
            cur = cur.next
            i += 1
        raise IndexError("Linked List index out of range")
    def sort(self):
        head = self.head
        new = ListNode(0)
        while head:
            cur = new
            while cur.next:
                if cur.next.val > head.val:
                    break
                cur = cur.next
            n = ListNode(val = head.val, next = cur.next)
            cur.next = n
            head = head.next
        self.head = new.next

    def __repr__(self):
        l = []
        cur = self.head
        while cur:
            l.append(str(cur.val))
            cur = cur.next
        return ' -> '.join(l)
    
    def append(self, val):
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = ListNode(val)

    def insert(self, k, val):
        i = -1
        cur = self.head
        while cur:
            if i == k:
                node = ListNode(val)
                node.next = cur.next
                cur.next = node
                return
            cur = cur.next
            i += 1
        raise IndexError("Linked List index out of range")

    def delete(self, k):
        i = 0
        cur = self.head
        while cur:
            if i == k:
                try:
                    cur.next = cur.next.next
                except:
                    cur.next = None
                return
            cur = cur.next
            i += 1
        raise IndexError("Linked List index out of range")

#Stacks
class stack:
    def __init__(self):
        self.stack = []
    def __repr__(self):
        return'\n'.join(self.stack[::-1])
    def __getitem__(self, k):
        try:
            return self.stack[k]
        except:
            raise IndexError("Stack index out of range")
    def push(self, val):
        self.stack.append(val)
    def pop(self):
        return self.stack.pop()
    def peek(self):
        return self.stack[-1]

#Quenes
class quene:
    def __init__(self):
        self.quene = []
    def __repr__(self):
        return' '.join(self.quene)
    def __getitem__(self, k):
        try:
            return self.quene[k]
        except:
            raise IndexError("Quene index out of range")
    def enquene(self, val):
        self.quene.append(val)
    def dequene(self):
        return self.stack.pop(0)

#Python heap
class heap:
    def __init__(self, cap):
        self.arr = []
        self.cap = cap

    def insert(self, val):
        if self.cap >= len(self.arr):
            self.arr.append(val)
            self.heapify_up()

    def delete(self):
        if len(self.arr):
            self.arr[0] = self.arr[-1]
            self.arr.pop()
            self.heapify_down()

    def heapify_up(self):
        i = len(self.arr) - 1
        while i >= 0 and self.arr[i] > min(self.arr[(i - 1) // 2], self.arr[(i - 2) // 2]):
            if self.arr[i] < self.arr[(i - 1) // 2]:
                self.arr[i], self.arr[(i - 1) // 2] = self.arr[(i - 1) // 2], self.arr[i]
                i = (i - 1) // 2
            else:
                self.arr[i], self.arr[(i - 2) // 2] = self.arr[(i - 2) // 2], self.arr[i]
                i = (i - 2) // 2

    def heapify_down(self):
        i = 0
        while i < len(self.arr) and self.arr[i] < max(self.arr[i * 2 + 1], self.arr[i * 2 + 2]):
            if i * 2 + 2 < len(self.arr):
                break
            if self.arr[i] < self.arr[i * 2 + 1]:
                self.arr[i], self.arr[1 * 2 + 1] = self.arr[i * 2 + 1], self.arr[i]
                i = i * 2 + 1
            else:
                self.arr[i], self.arr[1 * 2 + 2] = self.arr[i * 2 + 2], self.arr[i]
                i = i * 2 + 2





            
