#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

EXPECTED_DATE_PARTS = 3
MAX_MONTH = 12

INCOME_ARGS = 3
COST_CATEGORIES_ARGS = 2
COST_ARGS = 4
STATS_ARGS = 2

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != EXPECTED_DATE_PARTS:
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if 1 <= month <= MAX_MONTH and 1 <= day <= days_in_month[month - 1] and year >= 0:
        return day, month, year

    return None


def income_handler(amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    financial_transactions_storage.append({"amount": amount, "date": date_tuple})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    date_tuple = extract_date(income_date)
    if date_tuple is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    if "::" not in category_name:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    common, target = category_name.split("::", 1)
    if common not in EXPENSE_CATEGORIES or target not in EXPENSE_CATEGORIES[common]:
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": date_tuple})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = [f"{common}::{target}" for common, targets in EXPENSE_CATEGORIES.items() for target in targets]
    return "\n".join(categories)


def all_calculations(
    report_day: int, report_month: int, report_year: int
) -> tuple[float, float, float, dict[str, float]]:
    total = 0.0
    income = 0.0
    expenses = 0.0
    category_expenses: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if transaction == {}:
            continue
        if len(transaction["date"]) != EXPECTED_DATE_PARTS:
            continue
        day, month, year = transaction["date"]
        if (year, month, day) <= (report_year, report_month, report_day):
            if "category" not in transaction:
                total += transaction["amount"]
            else:
                total -= transaction["amount"]
        if (month, year) == (report_month, report_year):
            if "category" in transaction:
                expenses += transaction["amount"]
                target = transaction["category"].split("::", 1)[1]
                category_expenses[target] = category_expenses.get(target, 0.0) + transaction["amount"]
            else:
                income += transaction["amount"]

    return total, income, expenses, category_expenses


def stats_handler(report_date: str) -> str:
    report_date_tuple = extract_date(report_date)
    if report_date_tuple is None:
        return INCORRECT_DATE_MSG
    report_day, report_month, report_year = report_date_tuple

    total, income, expenses, category_expenses = all_calculations(report_day, report_month, report_year)

    if income >= expenses:
        profit = f"profit amounted to {(income - expenses):.2f} rubles."
    else:
        profit = f"loss amounted to {(expenses - income):.2f} rubles."

    outcome = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total:.2f} rubles",
        f"This month, the {profit}",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    if category_expenses:
        sorted_category_expenses = sorted(category_expenses.items())
        for i, (category, amount) in enumerate(sorted_category_expenses, 1):
            outcome.append(f"{i}. {category} : {amount:.2f}")

    return "\n".join(outcome)


def income_cmd_handler(parts: list[str]) -> None:
    if len(parts) != INCOME_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return
    amount = float(parts[1].replace(",", "."))
    date = parts[2]
    print(income_handler(amount, date))


def cost_cmd_handler(parts: list[str]) -> None:
    if len(parts) == COST_CATEGORIES_ARGS and parts[1] == "categories":
        print(cost_categories_handler())
        return
    if len(parts) != COST_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return

    category = parts[1]
    amount = float(parts[2].replace(",", "."))
    date = parts[3]

    outcome = cost_handler(category, amount, date)
    if outcome == NOT_EXISTS_CATEGORY:
        print(cost_categories_handler())
    else:
        print(outcome)


def stats_cmd_handler(parts: list[str]) -> None:
    if len(parts) != STATS_ARGS:
        print(UNKNOWN_COMMAND_MSG)
        return
    date = parts[1]
    print(stats_handler(date))


def main() -> None:
    while True:
        line = input()
        if not line:
            print(UNKNOWN_COMMAND_MSG)
            continue
        parts = line.split()
        cmd = parts[0]
        if cmd == "income":
            income_cmd_handler(parts)
        elif cmd == "cost":
            cost_cmd_handler(parts)
        elif cmd == "stats":
            stats_cmd_handler(parts)
        else:
            print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()
