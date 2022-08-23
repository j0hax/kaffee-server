// Package db allows for accessing the database.
//
// It also performs periodic maintenance.
package db

import "database/sql"

var (
	// DBCon is the connection handle
	// for the database
	DBCon *sql.DB
)
