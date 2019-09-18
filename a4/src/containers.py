'''
Containers to be used in the implementation of the calculator
'''


class Container:
    '''
    Super class for the different containers
    '''
    __slots__ = ['_items']

    def __init__(self):
        self._items = []

    def size(self):
        ''' Return size of container '''
        return len(self._items)

    def is_empty(self):
        ''' Check if container is empty '''
        return len(self._items) == 0

    def push(self, item):
        ''' Add item to container '''
        self._items += [item]

    def pop(self):
        ''' Retrieve next item from container '''
        raise NotImplementedError

    def peek(self):
        ''' Return, but don't remove, next item from container '''
        raise NotImplementedError


class Queue(Container):
    '''
    Implementation of a FIFO queue
    '''

    def pop(self):
        assert not self.is_empty()
        first_it, *self._items = self._items
        return first_it

    def peek(self):
        assert not self.is_empty()
        return self._items[0]


class Stack(Container):
    '''
    Implemntation of a stack
    '''

    def pop(self):
        assert not self.is_empty()
        return self._items.pop()

    def peek(self):
        assert not self.is_empty()
        return self._items[self.size() - 1]
