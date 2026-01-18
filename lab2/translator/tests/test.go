package main

import "fmt"

type Person struct {
	Name string
}

func (p Person) SayHi() {
	fmt.Println("Hi, I'm", p.Name)
}

type Rectangle struct {
	Width  int
	Height int
}

func main() {
	p := Person{Name: "Alice"}
	p.SayHi()

	for i := range 5 {
		fmt.Println("Counter:", i+1)
	}

	sum := 0
	for k := range 10 {
		sum += k + 1
	}
	fmt.Println("Sum 1 to 10:", sum)

	ch := make(chan string)

	msg := <-ch
	fmt.Println(msg)

	for j := range 10 {
		fmt.Println("Countdown:", 10-j)
	}

	defer fmt.Println("Deferred message 1")
	defer fmt.Println("Deferred message 2")

	fmt.Println("End of main")


}