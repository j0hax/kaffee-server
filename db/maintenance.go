package db

import (
	"log"

	"github.com/robfig/cron"
)

func Maintain() {
	c := cron.New()
	c.AddFunc("0 0 * * 0", vacuum)
}

// Vacuum optimizes the SQLite database file
func vacuum() {
	_, err := DBCon.Exec("VACUUM")
	if err != nil {
		log.Print(err)
	}
}

// CreateBackup creates a backup copy of the Database into the file determined by path
func CreateBackup(path string) {
	_, err := DBCon.Exec("VACUUM main INTO ?", path)
	if err != nil {
		log.Print(err)
	}
}
