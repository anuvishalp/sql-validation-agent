
import sqlite3
from sqlglot import parse_one
from sqlglot.errors import ParseError


def check_connection():
    """Check whether the practice database is accessible."""
    try:
        with sqlite3.connect("practice.db", timeout=5) as conn:
            conn.execute("SELECT 1")
        print("\n[PASS] Database connection is working.")
        return True
    except sqlite3.Error as error:
        print(f"\n[FAIL] Database connection: {error}")
        return False


def setup_sample_data():
    """Create a small sample table for learning."""
    with sqlite3.connect("practice.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                customer_name TEXT NOT NULL,
                city TEXT,
                status TEXT
            )
        """)

        conn.execute("""
            INSERT OR IGNORE INTO customers
            VALUES
                (1, 'Anita', 'Seattle', 'Active'),
                (2, 'Ravi', 'Bellevue', 'Active'),
                (3, 'John', 'Seattle', 'Inactive')
        """)


def validate_sql(sql):
    """Check SQL syntax, then safely test supported SELECT queries."""
    try:
        parse_one(sql, dialect="sqlite")
    except ParseError as error:
        return False, f"SQL syntax issue: {error}"

    # Only permit one read-only SELECT statement in this demo.
    try:
        with sqlite3.connect("practice.db", timeout=5) as conn:
            conn.execute("PRAGMA query_only = ON")
            conn.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
        return True, "SQL parsed and the query plan was accepted."
    except sqlite3.Error as error:
        return False, f"Database validation issue: {error}"


def main():
    print("===== SQL Validation Agent =====")

    setup_sample_data()

    if not check_connection():
        return

    print("\nPractice table: customers")
    print("Columns: customer_id, customer_name, city, status")

    sql = input("\nPaste your SQL query: ").strip()

    if not sql:
        print("Please enter a SQL query.")
        return

    # Enforce SELECT-only behavior in this beginner demo.
    try:
        parsed = parse_one(sql, dialect="sqlite")
    except ParseError as error:
        print(f"\n[INVALID] Syntax issue: {error}")
        print("\nExample of correct syntax:")
        print("SELECT customer_name FROM customers;")
        return

    if parsed.key.upper() != "SELECT":
        print("\n[BLOCKED] This demo accepts SELECT queries only.")
        print("Use a test database for write operations.")
        return

    valid, message = validate_sql(sql)

    print(f"\nValidation result: {message}")

    if not valid:
        print("\nPlease review the error and correct your query.")
        return

    print("\nWhat result do you expect from this query?")
    expected = input(
        "Describe the required data or result: "
    ).strip()

    print("\n===== Agent Review =====")
    print("SQL:", sql)
    print("Expected result:", expected or "Not provided")
    print("\nSuggestions:")

    if "expected" not in locals():
        return

    if expected:
        print(
            "Compare the query's selected columns, filters, "
            "joins and sorting with your expected result."
        )
        print("The agent has not yet verified that the result "
              "matches your business requirement.")
    else:
        print("Provide the expected columns and filtering rules "
              "for a more meaningful review.")

    print("\nExample query:")
    print("""
SELECT customer_name, city
FROM customers
WHERE status = 'Active'
ORDER BY customer_name;
""")


if __name__ == "__main__":
    main()
