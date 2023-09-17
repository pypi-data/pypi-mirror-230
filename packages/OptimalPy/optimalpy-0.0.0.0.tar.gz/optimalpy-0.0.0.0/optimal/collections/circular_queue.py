from collections import deque

class CircularQueue:
    def __init__(self, max_size):
        data = [None] * max_size
        self.__data = deque(data, max_size)
        self.__max_size = max_size

    def append(self, item):
        self.__data.appendleft(item)

    def first(self):
        return self.__data[self.__max_size - 1]

    def last(self):
        return self.__data[0]

    def get_data(self):
        return [item for item in self.__data]

    def __str__(self):
        return f"{self.get_data()}"
