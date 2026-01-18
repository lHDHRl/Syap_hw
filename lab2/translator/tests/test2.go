package main

import "fmt"

type Animal struct {
	Name  string
	Sound string
}

func (a Animal) Speak() {
	fmt.Printf("%s says %s\n", a.Name, a.Sound)
}

type Car struct {
	Brand string
	Model string
	Year  int
}

func main() {
	dog := Animal{Name: "Dog", Sound: "Woof"}
	dog.Speak()

	cat := Animal{Name: "Cat", Sound: "Meow"}
	cat.Speak()

	car := Car{Brand: "Toyota", Model: "Corolla", Year: 2020}
	fmt.Printf("Car: %s %s %d\n", car.Brand, car.Model, car.Year)

	for i := range 5 {
		fmt.Println("Loop iteration:", i)
	}

	product := 1
	for j := range 5 {
		product *= (j + 1)
	}
	fmt.Println("Product 1 to 5:", product)

	sum := 0
	for k := range 10 {
		sum += (k + 1)
	}
	fmt.Println("Sum 1 to 10:", sum)

	ch := make(chan int)


	val := <-ch
	fmt.Println("Received from channel:", val)

	for m := range 10 {
		fmt.Println("Countdown:", m)
	}

	defer fmt.Println("Deferred cleanup 1")
	defer fmt.Println("Deferred cleanup 2")
	defer fmt.Println("Deferred cleanup 3")

	fmt.Println("Before end")

}