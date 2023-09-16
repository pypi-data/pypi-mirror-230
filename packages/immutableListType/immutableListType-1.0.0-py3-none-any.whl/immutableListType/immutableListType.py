"""
FILE: immutableListType.py
Author: Roger Barker
License: 
MIT License

Copyright (c) 2023 Roger Barker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

class ImmutableList(list):
    """
    Class ImmutableList is intended to be an immutable list. 
    Assign values at instantiation and then use the list as is.

    Will not be able to push/pop/insert/append/remove/clear/index/sort/reverse.
    Useful when making classes with constant list values.
    """
    def __init__(self, *args) -> None:
        """Initialize ImmutableList."""
        self.list = list()
        self.extend(list(args))    
    
    def pop(self, *_) -> None:
        """Override list.pop. Perform NOOP."""
        pass
    def append(self, *_) -> None:
        """Override list.append. Perform NOOP."""
        pass
    def clear(self, *_) -> None:
        """Override list.clear. Perform NOOP."""
        pass
    def index(self, *_) -> None:
        """Override list.index. Perform NOOP."""
        pass
    def insert(self, *_) -> None:
        """Override list.insert. Perform NOOP."""
        pass
    def remove(self, *_) -> None:
        """Override list.remove. Perform NOOP."""
        pass
    def reverse(self, *_) -> None:
        """Override list.reverse. Perform NOOP."""
        pass
    def sort(self, *_) -> None:
        """Override list.sort. Perform NOOP."""
        pass
