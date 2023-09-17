class Counter:

    def __init__(self):
        global Count
        self.Count = 0

    def Add(self):
        global Count
        self.Count += 1

Counter = Counter()


