import queue
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass


# Package: main

@dataclass
class Book:
    Title: str
    Author: str
    Pages: int


def Read(b):
    print("Reading '%s' by %s, %d pages\n", b.Title, b.Author, b.Pages)

@dataclass
class Student:
    Name: str
    Grade: int


def Study(s):
    print("%s is studying for grade %d\n", s.Name, s.Grade)

def main():
    try:
        book = Book(Title="Go Programming", Author="John Doe", Pages=300)
        book.Read()
        student = Student(Name="Alice", Grade=10)
        student.Study()
        for i in range(len(6)):
            print("Sequence:", i + 1 * i + 1)
        total = 0
        for j in range(len(10)):
            total += j + 1 * 2
        print("Sum of even numbers 2 to 20:", total)
        factorial = 1
        for k in range(len(6)):
            factorial *= k + 1
        print("Factorial of 6:", factorial)
        ch = queue.Queue()
        message = ch.get()
        print("Message:", message)
        for n in range(len(20)):
            print("Reverse:", n)
        print("Main function end")
    finally:
        print("Third defer")
        print("Second defer")
        print("First defer")
