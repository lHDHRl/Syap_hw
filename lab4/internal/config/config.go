package config

import "time"

const (
	LinksFileName     = "Links.xlsx"
	ResultExcelFile   = "result.xlsx"
	ResultCSVFile     = "result.csv"
	SheetName         = "Лист1"
	RequestDelay      = 500 * time.Millisecond
	BaseURL           = "https://www.vesselfinder.com"
	VesselPath        = "/ru/vessels/details/"
	ShipLinkClass     = "a.ship-link"
	TitleSelector     = "h1.title"
	IMOMMSISelector   = "td.v3.v3np"
	TypeSelector      = "td.n3"
	AISTypeText       = "AIS тип"
)