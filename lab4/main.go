package main

import (
	"fmt"
	"log"
	"time"

	"github.com/SYAP/lab4/internal/config"
	"github.com/SYAP/lab4/internal/models"
	"github.com/SYAP/lab4/internal/parser"
	"github.com/SYAP/lab4/internal/reader"
	"github.com/SYAP/lab4/internal/saver"
)

func main() {
	urls, err := reader.ReadURLsFromExcel()
	if err != nil {
		log.Fatal(err)
	}

	results := []models.VesselData{}
	for _, url := range urls {
		fmt.Printf("Обработка: %s\n", url)
		vessel, err := parser.ProcessVesselLink(url)
		if err != nil {
			vessel = models.VesselData{
				URL:   url,
				Error: err.Error(),
			}
		}
		results = append(results, vessel)
		time.Sleep(config.RequestDelay)
	}

	saver.SaveResultsToExcel(results)
	saver.SaveResultsToCSV(results)

	fmt.Println("Обработка завершена. Результаты сохранены в result.xlsx и result.csv")
}