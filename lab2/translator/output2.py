import queue
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass


# Package: main

@dataclass
class Animal:
    Name: str
    Sound: str


def Speak(a):
    print("%s says %s\n", a.Name, a.Sound)

@dataclass
class Car:
    Brand: str
    Model: str
    Year: int


def main():
    try:
        dog = Animal(Name="Dog", Sound="Woof")
        dog.Speak()
        cat = Animal(Name="Cat", Sound="Meow")
        cat.Speak()
        car = Car(Brand="Toyota", Model="Corolla", Year=2020)
        print("Car: %s %s %d\n", car.Brand, car.Model, car.Year)
        for i in range(len(5)):
            print("Loop iteration:", i)
        product = 1
        for j in range(len(5)):
            product *= j + 1
        print("Product 1 to 5:", product)
        sum = 0
        for k in range(len(10)):
            sum += k + 1
        print("Sum 1 to 10:", sum)
        ch = queue.Queue()
        val = ch.get()
        print("Received from channel:", val)
        for m in range(len(10)):
            print("Countdown:", m)
        print("Before end")
    finally:
        print("Deferred cleanup 3")
        print("Deferred cleanup 2")
        print("Deferred cleanup 1")
