package saver

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"

	"github.com/SYAP/lab4/internal/config"
	"github.com/SYAP/lab4/internal/models"
	"github.com/xuri/excelize/v2"
)

func SaveResultsToExcel(results []models.VesselData) {
	f := excelize.NewFile()

	headers := []string{"Название", "IMO", "MMSI", "Тип", "Ссылка", "Ошибка"}
	for i, header := range headers {
		cell, _ := excelize.CoordinatesToCellName(i+1, 1)
		f.SetCellValue("Sheet1", cell, header)
	}

	for i, vessel := range results {
		row := i + 2
		f.SetCellValue("Sheet1", fmt.Sprintf("A%d", row), vessel.Name)
		f.SetCellValue("Sheet1", fmt.Sprintf("B%d", row), vessel.IMO)
		f.SetCellValue("Sheet1", fmt.Sprintf("C%d", row), vessel.MMSI)
		f.SetCellValue("Sheet1", fmt.Sprintf("D%d", row), vessel.Type)
		f.SetCellValue("Sheet1", fmt.Sprintf("E%d", row), vessel.URL)
		f.SetCellValue("Sheet1", fmt.Sprintf("F%d", row), vessel.Error)
	}

	if err := f.SaveAs(config.ResultExcelFile); err != nil {
		log.Fatal("Ошибка сохранения Excel файла:", err)
	}
}

func SaveResultsToCSV(results []models.VesselData) {
	file, err := os.Create(config.ResultCSVFile)
	if err != nil {
		log.Fatal("Ошибка создания CSV файла:", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	headers := []string{"Название", "IMO", "MMSI", "Тип", "Ссылка", "Ошибка"}
	writer.Write(headers)

	for _, vessel := range results {
		record := []string{
			vessel.Name,
			vessel.IMO,
			vessel.MMSI,
			vessel.Type,
			vessel.URL,
			vessel.Error,
		}
		writer.Write(record)
	}
}