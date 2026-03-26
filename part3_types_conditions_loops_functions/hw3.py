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

AMOUNT = "amount"
DATE = "date"
CATEGORY = "category"

# fmt:off
DAYS_IN_MONTH = [
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31
    ]
# fmt:on


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    if year % 4 == 0:
        if year % 100 == 0:
            return year % 400 == 0
        return True
    return False


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = maybe_dt.split("-")
    if len(parts) != EXPECTED_DATE_PARTS:
        return None
    day = int(parts[0])
    month = int(parts[1])
    year = int(parts[2])

    if is_leap_year(year):
        DAYS_IN_MONTH[1] = 29
    else:
        DAYS_IN_MONTH[1] = 28

    month_ok = 1 <= month <= MAX_MONTH
    day_ok = 1 <= day <= DAYS_IN_MONTH[month - 1]
    year_ok = year >= 0
    if month_ok and day_ok and year_ok:
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
    financial_transactions_storage.append({AMOUNT: amount, DATE: date_tuple})
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
    financial_transactions_storage.append(
        {CATEGORY: category_name, AMOUNT: amount, DATE: date_tuple}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    categories = [
        f"{common}::{target}"
        for common, targets in EXPENSE_CATEGORIES.items()
        for target in targets
    ]
    return "\n".join(categories)


def transaction_check(transaction: dict[str, Any]) -> bool:
    if not transaction:
        return False
    return len(transaction[DATE]) != EXPECTED_DATE_PARTS


def total_up_to_date(report_day: int, report_month: int, report_year: int) -> float:
    total = float(0)
    for transaction in financial_transactions_storage:
        if not transaction_check(transaction):
            continue
        day, month, year = transaction[DATE]
        if (year, month, day) <= (report_year, report_month, report_day):
            if CATEGORY in transaction:
                total -= transaction[AMOUNT]
            else:
                total += transaction[AMOUNT]
    return total


def month_stats(
    report_month: int, report_year: int
) -> tuple[float, float, dict[str, float]]:
    income = float(0)
    expenses = float(0)
    category_expenses: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction_check(transaction):
            continue
        date_tuple = transaction[DATE]
        month = date_tuple[1]
        year = date_tuple[2]
        if (month, year) == (report_month, report_year):
            if CATEGORY in transaction:
                amount = transaction[AMOUNT]
                expenses += amount
                category = transaction.get(CATEGORY, "just nothing")
                target = category.split("::", 1)[1]
                category_expenses[target] = (
                    category_expenses.get(target, float(0)) + amount
                )
            else:
                income += transaction[AMOUNT]
    return income, expenses, category_expenses


def profit_stats(income: float, expenses: float) -> str:
    if income >= expenses:
        return "profit amounted to {(income - expenses):.2f} rubles."
    return "loss amounted to {(expenses - income):.2f} rubles."


def outcome_changer(
    category_expenses: dict[str, float], outcome: list[str]
) -> list[str]:
    if category_expenses:
        sorted_category_expenses = sorted(category_expenses.items())
        for i, (category, amount) in enumerate(sorted_category_expenses, 1):
            outcome.append(f"{i}. {category} : {amount:.2f}")
    return outcome


def stats_handler(report_date: str) -> str:
    report_date_tuple = extract_date(report_date)
    if report_date_tuple is None:
        return INCORRECT_DATE_MSG
    report_day, report_month, report_year = report_date_tuple

    total = total_up_to_date(report_day, report_month, report_year)

    income, expenses, category_expenses = month_stats(report_month, report_year)

    profit = profit_stats(income, expenses)

    outcome = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total:.2f} rubles",
        f"This month, the {profit}",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    outcome_changer(category_expenses, outcome)

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


def cmd_checker(parts: list[str]) -> None:
    cmd = parts[0]
    if cmd == "income":
        income_cmd_handler(parts)
    elif cmd == "cost":
        cost_cmd_handler(parts)
    elif cmd == "stats":
        stats_cmd_handler(parts)
    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    while True:
        line = input()
        if not line:
            print(UNKNOWN_COMMAND_MSG)
            break
        cmd_checker(line.split())


if __name__ == "__main__":
    main()
