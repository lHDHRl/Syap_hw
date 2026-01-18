package reader

import (
	"fmt"

	"github.com/SYAP/lab4/internal/config"
	"github.com/xuri/excelize/v2"
)

func ReadURLsFromExcel() ([]string, error) {
	f, err := excelize.OpenFile(config.LinksFileName)
	if err != nil {
		return nil, fmt.Errorf("ошибка открытия файла %s: %v", config.LinksFileName, err)
	}
	defer f.Close()

	rows, err := f.GetRows(config.SheetName)
	if err != nil {
		return nil, fmt.Errorf("ошибка чтения листа %s: %v", config.SheetName, err)
	}

	var urls []string
	for i, row := range rows {
		if i == 0 || len(row) == 0 {
			continue
		}
		urls = append(urls, row[0])
	}

	fmt.Printf("Найдено %d ссылок для проверки\n", len(urls))
	return urls, nil
}