// Package users provides structures and functions for modifying users,
// balances, and transactions
package users

// Struct User represents a user from the database.
type User struct {
	Id         int
	Vip        bool
	System     bool
	Name       string
	LastUpdate float64

	transponder      string
	widthdrawalCount int
	depositCount     int
	withdrawalTotal  int
}

// DeleteUser deletes a user from the database.
func DeleteUser(id int) error {
	return nil
}

// UndoTransaction deletes the last transaction of a given user.
func UndoTransaction(id int) error {
	return nil
}

// GetUser retrieves a user from the database by their ID.
func GetUser(id int) error {
	return nil
}

// GetUserByName retrieves the first user whose name matches that of the database.
func GetUserByName(name string) error {
	return nil
}

// GetUsers retrieves all users from the database
func GetUsers() ([]User, error) {
	var result []User
	return result, nil
}

// SaveUser saves a new user to the database if they don't exist
// or, if the timestamp is newer, updates their data.
func SaveUser(user User) error {
	return nil
}

// SaveUsers compares and update users in the database.
// Essentially, this function calls SaveUser() for each user in the slice.
//
// Commonly used to merge cached data returned from a client.
func SaveUsers(users []User) error {
	return nil
}
