
import csv
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from collections import Counter


CSV_FILE = "library_records.csv"
JSON_FILE = "library_report.json"
GRAPH_DIR = "graphs"

FIELDS = [
    "loan_id", "student_id", "book_id", "book_title",
    "category", "issue_date", "due_date", "return_date"
]


# --------------------------------------------------
# 1. LOAN RECORD CLASS
# --------------------------------------------------

class LoanRecord:

    def __init__(self, loan_id, student_id, book_id,
                 book_title, category, issue_date,
                 due_date, return_date=""):

        self.loan_id = loan_id
        self.student_id = student_id
        self.book_id = book_id
        self.book_title = book_title
        self.category = category
        self.issue_date = issue_date
        self.due_date = due_date
        self.return_date = return_date

    def to_dict(self):

        return {
            "loan_id": self.loan_id,
            "student_id": self.student_id,
            "book_id": self.book_id,
            "book_title": self.book_title,
            "category": self.category,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "return_date": self.return_date
        }


# --------------------------------------------------
# 2. CSV FILE HANDLING
# --------------------------------------------------

def create_sample_csv():

    if os.path.exists(CSV_FILE):
        return

    data = [
        ["L001", "S101", "B101", "Python Basics",
         "Technology", "2026-01-05", "2026-01-19", "2026-01-15"],

        ["L002", "S102", "B102", "The Blue Umbrella",
         "Fiction", "2026-01-10", "2026-01-24", "2026-01-22"],

        ["L003", "S103", "B103", "Concepts of Physics",
         "Science", "2026-02-02", "2026-02-16", "2026-02-12"],

        ["L004", "S104", "B101", "Python Basics",
         "Technology", "2026-02-08", "2026-02-22", "2026-02-20"],

        ["L005", "S105", "B104", "A Brief History of Time",
         "Science", "2026-03-01", "2026-03-15", "2026-03-12"],

        ["L006", "S101", "B105", "Wings of Fire",
         "Biography", "2026-03-10", "2026-03-24", "2026-03-23"],

        ["L007", "S106", "B102", "The Blue Umbrella",
         "Fiction", "2026-04-03", "2026-04-17", "2026-04-14"],

        ["L008", "S107", "B106", "Digital Electronics",
         "Technology", "2026-04-10", "2026-04-24", ""]
    ]

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)
        writer.writerow(FIELDS)
        writer.writerows(data)


def load_records():

    records = []

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:

            record = LoanRecord(
                row["loan_id"],
                row["student_id"],
                row["book_id"],
                row["book_title"],
                row["category"],
                row["issue_date"],
                row["due_date"],
                row["return_date"]
            )

            records.append(record)

    return records


def save_records(records):

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        for record in records:
            writer.writerow(record.to_dict())


def get_dataframe(records):

    return pd.DataFrame(
        [record.to_dict() for record in records],
        columns=FIELDS
    )


# --------------------------------------------------
# 3. ADD NEW LOAN RECORD
# --------------------------------------------------

def add_record(records):

    print("\n--- ADD NEW LOAN RECORD ---")

    loan_id = input("Enter Loan ID: ").strip()

    if any(r.loan_id == loan_id for r in records):
        print("Loan ID already exists!")
        return

    student_id = input("Enter Student ID: ").strip()
    book_id = input("Enter Book ID: ").strip()
    book_title = input("Enter Book Title: ").strip()
    category = input("Enter Book Category: ").strip()

    issue_date = input("Enter Issue Date (YYYY-MM-DD): ").strip()
    due_date = input("Enter Due Date (YYYY-MM-DD): ").strip()
    return_date = input(
        "Enter Return Date (YYYY-MM-DD, leave blank if not returned): "
    ).strip()

    try:

        issue = datetime.strptime(issue_date, "%Y-%m-%d").date()
        due = datetime.strptime(due_date, "%Y-%m-%d").date()

        if due < issue:
            print("Due date cannot be before issue date!")
            return

        if return_date:

            returned = datetime.strptime(
                return_date, "%Y-%m-%d"
            ).date()

            if returned < issue:
                print("Return date cannot be before issue date!")
                return

    except ValueError:

        print("Invalid date format!")
        return

    if not all([loan_id, student_id, book_id,
                book_title, category, issue_date, due_date]):

        print("Required fields cannot be empty!")
        return

    record = LoanRecord(
        loan_id, student_id, book_id, book_title,
        category, issue_date, due_date, return_date
    )

    records.append(record)
    save_records(records)

    print("Record added successfully!")


# --------------------------------------------------
# 4. DISPLAY ALL RECORDS
# --------------------------------------------------

def display_records(records):

    if not records:
        print("\nNo records available!")
        return

    df = get_dataframe(records)

    print("\n--- ALL LIBRARY RECORDS ---")
    print(df.to_string(index=False))


# --------------------------------------------------
# 5. SEARCH RECORDS
# --------------------------------------------------

def search_records(records):

    term = input(
        "\nEnter Loan ID, Student ID, Book ID or Book Title: "
    ).strip().lower()

    matches = []

    for r in records:

        values = [
            r.loan_id, r.student_id, r.book_id,
            r.book_title, r.category
        ]

        if any(term in value.lower() for value in values):
            matches.append(r)

    if matches:
        display_records(matches)
    else:
        print("No matching records found!")


# --------------------------------------------------
# 6. LOAN DURATION USING NUMPY
# --------------------------------------------------

def calculate_durations(records):

    durations = []
    labels = []

    for r in records:

        try:

            start = datetime.strptime(
                r.issue_date, "%Y-%m-%d"
            ).date()

            if r.return_date:

                end = datetime.strptime(
                    r.return_date, "%Y-%m-%d"
                ).date()

            else:
                end = date.today()

            durations.append((end - start).days)
            labels.append(r.loan_id)

        except ValueError:
            continue

    if not durations:
        print("No valid loan dates available!")
        return

    arr = np.array(durations)

    print("\n--- LOAN DURATION ANALYSIS ---")

    for i in range(len(arr)):
        print(labels[i], ":", arr[i], "days")

    print("Average Duration:", round(np.mean(arr), 2), "days")
    print("Shortest Duration:", np.min(arr), "days")
    print("Longest Duration:", np.max(arr), "days")


# --------------------------------------------------
# 7. OVERDUE BOOK CHECKING
# --------------------------------------------------

def check_overdue(records):

    today = date.today()
    overdue = []

    for r in records:

        if not r.return_date:

            try:

                due = datetime.strptime(
                    r.due_date, "%Y-%m-%d"
                ).date()

                if due < today:
                    overdue.append(r)

            except ValueError:
                continue

    print("\n--- OVERDUE BOOKS ---")

    if not overdue:
        print("No overdue books found!")
        return

    for r in overdue:

        due = datetime.strptime(
            r.due_date, "%Y-%m-%d"
        ).date()

        days = (today - due).days

        print(
            r.book_title,
            "| Student:", r.student_id,
            "| Days Overdue:", days
        )


# --------------------------------------------------
# 8. BORROWING FREQUENCY
# --------------------------------------------------

def borrowing_frequency(records):

    if not records:
        print("No records available!")
        return

    counts = Counter(
        r.book_title for r in records
    )

    print("\n--- BOOK BORROWING FREQUENCY ---")

    for title, count in counts.most_common():

        print(title, ":", count, "times")

    most = counts.most_common(1)[0]

    print("\nMost Borrowed Book:", most[0])
    print("Total Borrowings:", most[1])


# --------------------------------------------------
# 9. CATEGORY-WISE ANALYSIS USING PANDAS
# --------------------------------------------------

def category_summary(records):

    if not records:
        print("No records available!")
        return

    df = get_dataframe(records)

    summary = df.groupby("category").size()

    print("\n--- CATEGORY-WISE SUMMARY ---")
    print(summary.to_string())

    print("\nHighest Demand Category:", summary.idxmax())


# --------------------------------------------------
# 10. MONTHLY BORROWING SUMMARY
# --------------------------------------------------

def monthly_summary(records):

    if not records:
        print("No records available!")
        return

    df = get_dataframe(records)

    df["issue_date"] = pd.to_datetime(
        df["issue_date"], errors="coerce"
    )

    df = df.dropna(subset=["issue_date"])

    df["month"] = df["issue_date"].dt.to_period("M")

    summary = df.groupby("month").size()

    print("\n--- MONTHLY BORROWING SUMMARY ---")
    print(summary.to_string())


# --------------------------------------------------
# 11. DUPLICATE AND INCOMPLETE RECORD DETECTION
# --------------------------------------------------

def check_data_quality(records):

    seen = set()
    duplicates = []
    incomplete = []
    invalid_dates = []

    for r in records:

        if r.loan_id in seen:
            duplicates.append(r.loan_id)

        seen.add(r.loan_id)

        required = [
            r.loan_id, r.student_id, r.book_id,
            r.book_title, r.category,
            r.issue_date, r.due_date
        ]

        if not all(required):
            incomplete.append(r.loan_id)

        try:

            issue = datetime.strptime(
                r.issue_date, "%Y-%m-%d"
            ).date()

            due = datetime.strptime(
                r.due_date, "%Y-%m-%d"
            ).date()

            if due < issue:
                invalid_dates.append(r.loan_id)

            if r.return_date:

                returned = datetime.strptime(
                    r.return_date, "%Y-%m-%d"
                ).date()

                if returned < issue:
                    invalid_dates.append(r.loan_id)

        except ValueError:
            invalid_dates.append(r.loan_id)

    print("\n--- DATA QUALITY REPORT ---")

    print("Duplicate Loan IDs:",
          duplicates if duplicates else "None")

    print("Incomplete Records:",
          incomplete if incomplete else "None")

    print("Invalid Dates:",
          invalid_dates if invalid_dates else "None")


# --------------------------------------------------
# 12. DATA VISUALIZATION USING MATPLOTLIB
# --------------------------------------------------

def generate_graphs(records):

    if not records:
        print("No records available!")
        return

    os.makedirs(GRAPH_DIR, exist_ok=True)

    df = get_dataframe(records)

    # Category-wise bar graph

    category = df["category"].value_counts()

    plt.figure(figsize=(9, 5))

    category.plot(kind="bar")

    plt.title("Library Borrowing by Category")
    plt.xlabel("Book Category")
    plt.ylabel("Number of Loans")

    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(
        os.path.join(GRAPH_DIR, "category_analysis.png")
    )

    plt.show()
    plt.close()

    # Monthly borrowing trend

    df["issue_date"] = pd.to_datetime(
        df["issue_date"], errors="coerce"
    )

    df = df.dropna(subset=["issue_date"])

    df["month"] = df["issue_date"].dt.to_period("M")

    monthly = df.groupby("month").size()

    if not monthly.empty:

        plt.figure(figsize=(9, 5))

        plt.plot(
            monthly.index.astype(str),
            monthly.values,
            marker="o"
        )

        plt.title("Monthly Library Borrowing Trend")
        plt.xlabel("Month")
        plt.ylabel("Number of Loans")

        plt.xticks(rotation=30)
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(
            os.path.join(GRAPH_DIR, "monthly_trends.png")
        )

        plt.show()
        plt.close()

    print("Graphs saved successfully in the graphs folder!")


# --------------------------------------------------
# 13. JSON REPORT EXPORT
# --------------------------------------------------

def export_json(records):

    df = get_dataframe(records)

    category = df.groupby("category").size().to_dict()

    df["issue_date"] = pd.to_datetime(
        df["issue_date"], errors="coerce"
    )

    df = df.dropna(subset=["issue_date"])

    df["month"] = df["issue_date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month").size().to_dict()

    report = {

        "generated_on": date.today().isoformat(),

        "total_loan_records": len(records),

        "category_summary": category,

        "monthly_summary": monthly,

        "loan_records": [
            r.to_dict() for r in records
        ]
    }

    with open(JSON_FILE, "w", encoding="utf-8") as f:

        json.dump(report, f, indent=4)

    print("JSON report exported successfully!")


# --------------------------------------------------
# 14. MAIN MENU
# --------------------------------------------------

def show_menu():

    print("\n" + "=" * 50)

    print(" LIBRARY CIRCULATION AND DEMAND DASHBOARD ")

    print("=" * 50)

    print("1. Add a New Loan Record")
    print("2. Display All Loan Records")
    print("3. Search Loan Records")
    print("4. Calculate Loan Durations")
    print("5. Check Overdue Books")
    print("6. Analyse Borrowing Frequency")
    print("7. Generate Category-wise Summary")
    print("8. Generate Monthly Borrowing Summary")
    print("9. Detect Duplicate and Incomplete Records")
    print("10. Generate Graphs and Charts")
    print("11. Export Report to JSON")
    print("12. Exit")

    print("=" * 50)


# --------------------------------------------------
# 15. MAIN FUNCTION
# --------------------------------------------------

def main():

    create_sample_csv()

    records = load_records()

    print("\nWelcome to the Library Dashboard!")

    while True:

        show_menu()

        choice = input("Enter your choice (1-12): ").strip()

        if choice == "1":
            add_record(records)

        elif choice == "2":
            display_records(records)

        elif choice == "3":
            search_records(records)

        elif choice == "4":
            calculate_durations(records)

        elif choice == "5":
            check_overdue(records)

        elif choice == "6":
            borrowing_frequency(records)

        elif choice == "7":
            category_summary(records)

        elif choice == "8":
            monthly_summary(records)

        elif choice == "9":
            check_data_quality(records)

        elif choice == "10":
            generate_graphs(records)

        elif choice == "11":
            export_json(records)

        elif choice == "12":

            print("\nThank you for using the Library Dashboard!")

            break

        else:

            print("Invalid choice! Please try again.")


# --------------------------------------------------
# PROGRAM EXECUTION
# --------------------------------------------------

if __name__ == "__main__":

    main()
