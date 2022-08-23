package users

// Struct Transaction represents a transaction (flow of credit and debit).
type Transaction struct {
	User        int
	Amount      int
	Description string
	Timestamp   float64
}

// GetTransactions returns a list of the last n transactions.
func GetTransactions(n int) ([]Transaction, error) {
	var result []Transaction
	return result, nil
}

// TotalIntake returns the sum of money paid by users.
//
// Note that system users are excluded.
func TotalIntake() (int, error) {
	return 0, nil
}

// TotalDebt returns the sum balances of users in debt.
//
// Note that system users are excluded.
func TotalDebt() (int, error) {
	return 0, nil
}

// SumTransactions sums all user transactions.
//
// Note that system users are excluded.
func SumTransactions() (int, error) {
	return 0, nil
}

// InsertTransaction adds a new transaction to the database
func InsertTransaction(t Transaction) error {
	return nil
}

// InsertTransactions compares and updates transaction in the database.
// Essentially, this function calls InsertTransaction() for each transaction in the slice.
func InsertTransactions() error {
	return nil
}
