package parser

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"github.com/SYAP/lab4/internal/config"
	"github.com/SYAP/lab4/internal/models"
)

func ProcessVesselLink(url string) (models.VesselData, error) {
	resp, err := http.Get(url)
	if err != nil {
		return models.VesselData{}, fmt.Errorf("ошибка HTTP запроса: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return models.VesselData{}, fmt.Errorf("статус код: %d", resp.StatusCode)
	}

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return models.VesselData{}, fmt.Errorf("ошибка парсинга HTML: %v", err)
	}

	var vesselLinks []string
	doc.Find(config.ShipLinkClass).Each(func(i int, s *goquery.Selection) {
		href, exists := s.Attr("href")
		if exists && strings.Contains(href, config.VesselPath) {
			fullURL := config.BaseURL + href
			vesselLinks = append(vesselLinks, fullURL)
		}
	})

	if len(vesselLinks) == 0 {
		return models.VesselData{URL: url}, fmt.Errorf("суда не найдены")
	}

	vesselURL := vesselLinks[0]
	if len(vesselLinks) > 1 {
		fmt.Printf("  Найдено %d судов, берем первое: %s\n", len(vesselLinks), vesselURL)
	}

	return GetVesselDetails(vesselURL, url)
}

func GetVesselDetails(vesselURL, originalURL string) (models.VesselData, error) {
	resp, err := http.Get(vesselURL)
	if err != nil {
		return models.VesselData{}, fmt.Errorf("ошибка HTTP запроса на страницу судна: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return models.VesselData{}, fmt.Errorf("статус код страницы судна: %d", resp.StatusCode)
	}

	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return models.VesselData{}, fmt.Errorf("ошибка парсинга HTML страницы судна: %v", err)
	}

	name := ""
	doc.Find(config.TitleSelector).Each(func(i int, s *goquery.Selection) {
		if i == 0 {
			name = strings.TrimSpace(s.Text())
		}
	})

	imoMMSI := ""
	doc.Find(config.IMOMMSISelector).Each(func(i int, s *goquery.Selection) {
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
	doc.Find(config.TypeSelector).Each(func(i int, s *goquery.Selection) {
		if strings.TrimSpace(s.Text()) == config.AISTypeText {
			nextTd := s.Next()
			if nextTd.Length() > 0 {
				vesselType = strings.TrimSpace(nextTd.Text())
			}
		}
	})

	if name == "" || imo == "" || mmsi == "" || vesselType == "" {
		return models.VesselData{URL: originalURL}, fmt.Errorf("не все данные найдены: name='%s', imo='%s', mmsi='%s', type='%s'",
			name, imo, mmsi, vesselType)
	}

	return models.VesselData{
		Name: name,
		IMO:  imo,
		MMSI: mmsi,
		Type: vesselType,
		URL:  originalURL,
	}, nil
}