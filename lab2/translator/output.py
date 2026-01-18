import queue
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass


# Package: main

@dataclass
class Person:
    Name: str


def SayHi(p):
    print("Hi, I'm", p.Name)

@dataclass
class Rectangle:
    Width: int
    Height: int


def main():
    try:
        p = Person(Name="Alice")
        p.SayHi()
        for i in range(len(5)):
            print("Counter:", i + 1)
        sum = 0
        for k in range(len(10)):
            sum += k + 1
        print("Sum 1 to 10:", sum)
        ch = queue.Queue()
        msg = ch.get()
        print(msg)
        for j in range(len(10)):
            print("Countdown:", 10 - j)
        print("End of main")
    finally:
        print("Deferred message 2")
        print("Deferred message 1")
