package main

import "fmt"

type Book struct {
	Title  string
	Author string
	Pages  int
}

func (b Book) Read() {
	fmt.Printf("Reading '%s' by %s, %d pages\n", b.Title, b.Author, b.Pages)
}

type Student struct {
	Name  string
	Grade int
}

func (s Student) Study() {
	fmt.Printf("%s is studying for grade %d\n", s.Name, s.Grade)
}

func main() {
	book := Book{Title: "Go Programming", Author: "John Doe", Pages: 300}
	book.Read()

	student := Student{Name: "Alice", Grade: 10}
	student.Study()

	for i := range 6 {
		fmt.Println("Sequence:", (i+1)*(i+1))
	}

	total := 0
	for j := range 10 {
		total += (j + 1) * 2
	}
	fmt.Println("Sum of even numbers 2 to 20:", total)

	factorial := 1
	for k := range 6 {
		factorial *= (k + 1)
	}
	fmt.Println("Factorial of 6:", factorial)

	ch := make(chan string)


	message := <-ch
	fmt.Println("Message:", message)

	for n := range 20 {
		fmt.Println("Reverse:", n)
	}

	defer fmt.Println("First defer")
	defer fmt.Println("Second defer")
	defer fmt.Println("Third defer")

	fmt.Println("Main function end")

}