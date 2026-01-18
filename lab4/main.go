package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	"github.com/xuri/excelize/v2"
)

type VesselData struct {
	Name  string
	IMO   string
	MMSI  string
	Type  string
	URL   string
	Error string
}

func main() {
	f, err := excelize.OpenFile("Links.xlsx")
	if err != nil {
		log.Fatal("Ошибка открытия файла Links.xlsx:", err)
	}
	defer f.Close()

	rows, err := f.GetRows("Лист1")
	if err != nil {
		log.Fatal("Ошибка чтения листа:", err)
	}

	var urls []string
	for i, row := range rows {
		if i == 0 || len(row) == 0 {
			continue
		}
		urls = append(urls, row[0])
	}

	fmt.Printf("Найдено %d ссылок для проверки\n", len(urls))

	results := []VesselData{}
	for _, url := range urls {
		fmt.Printf("Обработка: %s\n", url)
		vessel, err := processVesselLink(url)
		if err != nil {
			vessel = VesselData{
				URL:   url,
				Error: err.Error(),
			}
		}
		results = append(results, vessel)
		time.Sleep(500 * time.Millisecond)
	}

	saveResultsToExcel(results)

	saveResultsToCSV(results)

	fmt.Println("Обработка завершена. Результаты сохранены в result.xlsx и result.csv")
}

func processVesselLink(url string) (VesselData, error) {
	resp, err := http.Get(url)
	if err != nil {
		return VesselData{}, fmt.Errorf("ошибка HTTP запроса: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return VesselData{}, fmt.Errorf("статус код: %d", resp.StatusCode)
	}

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return VesselData{}, fmt.Errorf("ошибка парсинга HTML: %v", err)
	}

	var vesselLinks []string
	doc.Find("a.ship-link").Each(func(i int, s *goquery.Selection) {
		href, exists := s.Attr("href")
		if exists && strings.Contains(href, "/ru/vessels/details/") {
			fullURL := "https://www.vesselfinder.com" + href
			vesselLinks = append(vesselLinks, fullURL)
		}
	})

	if len(vesselLinks) == 0 {
		return VesselData{URL: url}, fmt.Errorf("суда не найдены")
	}

	vesselURL := vesselLinks[0]
	if len(vesselLinks) > 1 {
		fmt.Printf("  Найдено %d судов, берем первое: %s\n", len(vesselLinks), vesselURL)
	}

	return getVesselDetails(vesselURL, url)
}

func getVesselDetails(vesselURL, originalURL string) (VesselData, error) {
	resp, err := http.Get(vesselURL)
	if err != nil {
		return VesselData{}, fmt.Errorf("ошибка HTTP запроса на страницу судна: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return VesselData{}, fmt.Errorf("статус код страницы судна: %d", resp.StatusCode)
	}

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return VesselData{}, fmt.Errorf("ошибка парсинга HTML страницы судна: %v", err)
	}

	name := ""
	doc.Find("h1.title").Each(func(i int, s *goquery.Selection) {
		if i == 0 {
			name = strings.TrimSpace(s.Text())
		}
	})

	imoMMSI := ""
	doc.Find("td.v3.v3np").Each(func(i int, s *goquery.Selection) {
		if strings.Contains(s.Parent().Text(), "IMO / MMSI") {
			imoMMSI = strings.TrimSpace(s.Text())
		}
	})

	imo, mmsi := "", ""
	if imoMMSI != "" {
		parts := strings.Split(imoMMSI, "/")
		if len(parts) >= 2 {
			imo = strings.TrimSpace(parts[0])
			mmsi = strings.TrimSpace(parts[1])
		}
	}

	vesselType := ""
	doc.Find("td.n3").Each(func(i int, s *goquery.Selection) {
		if strings.TrimSpace(s.Text()) == "AIS тип" {
			nextTd := s.Next()
			if nextTd.Length() > 0 {
				vesselType = strings.TrimSpace(nextTd.Text())
			}
		}
	})

	if name == "" || imo == "" || mmsi == "" || vesselType == "" {
		return VesselData{URL: originalURL}, fmt.Errorf("не все данные найдены: name='%s', imo='%s', mmsi='%s', type='%s'",
			name, imo, mmsi, vesselType)
	}

	return VesselData{
		Name: name,
		IMO:  imo,
		MMSI: mmsi,
		Type: vesselType,
		URL:  originalURL,
	}, nil
}

func saveResultsToExcel(results []VesselData) {
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

	if err := f.SaveAs("result.xlsx"); err != nil {
		log.Fatal("Ошибка сохранения Excel файла:", err)
	}
}

func saveResultsToCSV(results []VesselData) {
	file, err := os.Create("result.csv")
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