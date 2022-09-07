#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

class RepeaterIterator:
    def __init__(self, source):
        self.source = source

    def __next__(self):
        return self.source.value

class Repeater:
    def __init__(self, value):
        self.value = value

    def __iter__(self):
        return RepeaterIterator(self)

class BoundedRepeater:
    def __init__(self, value, max_repeats):
        self.value = value
        self.max_repeats = max_repeats
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.max_repeats:
            raise StopIteration
        self.count += 1
        return self.value

if __name__ == '__main__':

    if len(sys.argv) != 1:
        print('t_iter.py')
        quit()

    '''
    repeater = Repeater('Hello')
    for item in repeater:
        print(item)
    '''

    repeater = BoundedRepeater('Hello', 3)
    for item in repeater:
        print(item)
