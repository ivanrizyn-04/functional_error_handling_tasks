"""
Обробка помилок у функціональному стилі
Мова: Python

Файл містить рішення завдань 1-15.
Основна ідея: замість того, щоб кидати винятки назовні, функції повертають
явний результат: Option або Result.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Generic, TypeVar


T = TypeVar("T")
U = TypeVar("U")


# ============================================================
# Завдання 1. Аналіз коду
# ============================================================

def divide(a: float, b: float) -> float:
    return a / b


"""
Що станеться при b = 0?

divide(10, 0) викличе помилку:
ZeroDivisionError: division by zero

Переписування через try/except:
"""

def divide_with_try_except(a: float, b: float) -> float | None:
    try:
        return a / b
    except ZeroDivisionError:
        print("Помилка: ділення на нуль")
        return None


"""
Недоліки try/except-підходу:

1. Прихована логіка
   З типу функції не очевидно, що вона може завершитися помилкою.
   Зовнішній код має знати про винятки або спеціальні значення на кшталт None.

2. Побічні ефекти
   Функція не тільки обчислює результат, а ще й друкує повідомлення.
   Це ускладнює тестування та повторне використання.

3. Складність композиції
   Якщо результат однієї функції треба передати в іншу, доводиться постійно
   перевіряти None або ловити винятки на різних рівнях програми.
"""


# ============================================================
# Завдання 2. Safe-функція
# ============================================================

def safe_divide_tuple(a: float, b: float) -> tuple[str, float | str]:
    """
    Не кидає виняток назовні.
    Повертає:
    - ("ok", result)
    - ("error", "division by zero")
    """
    if b == 0:
        return ("error", "division by zero")

    return ("ok", a / b)


# ============================================================
# Завдання 3. Реалізація Option
# ============================================================

class Some(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def __repr__(self) -> str:
        return f"Some({self.value!r})"

    # Завдання 5. Map для Option
    def map(self, func: Callable[[T], U]) -> "Some[U]":
        return Some(func(self.value))


class Nothing:
    def __repr__(self) -> str:
        return "Nothing()"

    # Завдання 5. Map для Option
    def map(self, func: Callable[[Any], Any]) -> "Nothing":
        return self


Option = Some[T] | Nothing


# ============================================================
# Завдання 4. Safe-функція з Option
# ============================================================

def safe_divide_option(a: float, b: float) -> Option[float]:
    """
    Повертає:
    - Some(result), якщо ділення можливе
    - Nothing(), якщо ділення неможливе
    """
    if b == 0:
        return Nothing()

    return Some(a / b)


# ============================================================
# Завдання 6. Ланцюжок обчислень з Option
# ============================================================

def option_chain_example() -> Option[float]:
    return (
        safe_divide_option(10, 2)
        .map(lambda x: x * 2)
        .map(lambda x: x + 5)
    )


def option_chain_error_example() -> Option[float]:
    return (
        safe_divide_option(10, 0)
        .map(lambda x: x * 2)
        .map(lambda x: x + 5)
    )


# ============================================================
# Завдання 7. Реалізація Result
# ============================================================

class Ok(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"

    # Завдання 9. Map для Result
    def map(self, func: Callable[[T], U]) -> "Ok[U]":
        return Ok(func(self.value))

    # Завдання 10. FlatMap
    def flat_map(self, func: Callable[[T], "Result[U]"]) -> "Result[U]":
        return func(self.value)


class Error:
    def __init__(self, message: str | list[str]):
        self.message = message

    def __repr__(self) -> str:
        return f"Error({self.message!r})"

    # Завдання 9. Map для Result
    def map(self, func: Callable[[Any], Any]) -> "Error":
        return self

    # Завдання 10. FlatMap
    def flat_map(self, func: Callable[[Any], "Result[Any]"]) -> "Error":
        return self


Result = Ok[T] | Error


# ============================================================
# Завдання 8. Safe-функція з Result
# ============================================================

def safe_divide(a: float, b: float) -> Result[float]:
    """
    Повертає:
    - Ok(value)
    - Error(message)
    """
    if b == 0:
        return Error("division by zero")

    return Ok(a / b)


# ============================================================
# Завдання 11. Pipeline без try/except
# ============================================================

def safe_pipeline(x: float) -> Result[float]:
    return (
        safe_divide(x, 2)
        .map(lambda x: x + 10)
        .flat_map(lambda x: safe_divide(x, 0))
    )


"""
Для safe_pipeline(10) результат буде:

safe_divide(10, 2)        -> Ok(5.0)
.map(lambda x: x + 10)    -> Ok(15.0)
.flat_map(lambda x: safe_divide(x, 0)) -> Error("division by zero")

Отже:
- результат: Error("division by zero")
- pipeline зупиниться на flat_map, де викликається safe_divide(x, 0)
"""


# ============================================================
# Допоміжні функції для завдань 12 і 15
# ============================================================

def parse_int(value: Any) -> Result[int]:
    """
    Перетворення в int без try/except.

    Працює для:
    - int
    - рядків типу "25", "-10", "+7"

    Не використовує int(value), доки формат не перевірено регулярним виразом.
    """
    if isinstance(value, int):
        return Ok(value)

    if isinstance(value, str):
        text = value.strip()
        if re.fullmatch(r"[+-]?\d+", text):
            return Ok(int(text))

    return Error(f"cannot parse integer: {value!r}")


def require_greater_than(min_value: int) -> Callable[[int], Result[int]]:
    def validator(value: int) -> Result[int]:
        if value > min_value:
            return Ok(value)

        return Error(f"value must be greater than {min_value}")

    return validator


def require_at_least(min_value: int) -> Callable[[int], Result[int]]:
    def validator(value: int) -> Result[int]:
        if value >= min_value:
            return Ok(value)

        return Error(f"value must be at least {min_value}")

    return validator


# ============================================================
# Завдання 12. Обробка користувача без try/except
# ============================================================

def validate_user_age(user: dict[str, Any]) -> Result[int]:
    """
    Умова:
    user = {"age": "25"}

    Потрібно:
    - перетворити age у int
    - перевірити, що age > 18
    - без try/except
    """
    if "age" not in user:
        return Error("age is required")

    return (
        parse_int(user["age"])
        .flat_map(require_greater_than(18))
    )


# ============================================================
# Завдання 13. Обробка файлу
# ============================================================

FAKE_FILE_SYSTEM = {
    "hello.txt": "Hello, world!",
    "data.txt": "100\n200\n300",
}


def read_file(name: str) -> Result[str]:
    """
    Імітація читання файлу.

    Повертає:
    - Ok(content)
    - Error("file not found")
    """
    if name in FAKE_FILE_SYSTEM:
        return Ok(FAKE_FILE_SYSTEM[name])

    return Error("file not found")


# ============================================================
# Завдання 14. Multiple validations
# ============================================================

def validate_user_all_errors(user: dict[str, Any]) -> Result[dict[str, Any]]:
    """
    Умова:
    user = {
        "name": "Alice",
        "age": 17
    }

    Потрібно перевірити:
    - name не пустий
    - age >= 18

    P.S. повернути всі помилки
    """
    errors: list[str] = []

    name = user.get("name")
    age = user.get("age")

    if not isinstance(name, str) or name.strip() == "":
        errors.append("name must not be empty")

    age_result = parse_int(age)
    if isinstance(age_result, Error):
        errors.append(str(age_result.message))
    elif age_result.value < 18:
        errors.append("age must be at least 18")

    if errors:
        return Error(errors)

    return Ok({
        "name": name.strip(),
        "age": age_result.value,
    })


# ============================================================
# Завдання 15. Data processing pipeline
# ============================================================

transactions = [
    {"amount": "100"},
    {"amount": "abc"},
    {"amount": "200"},
]


def validate_positive(value: int) -> Result[int]:
    if value > 0:
        return Ok(value)

    return Error("amount must be greater than 0")


def parse_transaction_amount(transaction: dict[str, Any], index: int) -> Result[int]:
    if "amount" not in transaction:
        return Error(f"transaction #{index}: amount is required")

    return (
        parse_int(transaction["amount"])
        .flat_map(validate_positive)
        .map(lambda amount: amount)
    )


def sum_transactions(transactions_list: list[dict[str, Any]]) -> Result[int]:
    """
    Pipeline:
    1. parse int
    2. перевірити > 0
    3. підсумувати

    Всі помилки обробляються через Result.
    Якщо є помилки, повертається Error зі списком усіх помилок.
    """
    total = 0
    errors: list[str] = []

    for index, transaction in enumerate(transactions_list, start=1):
        result = parse_transaction_amount(transaction, index)

        if isinstance(result, Ok):
            total += result.value
        else:
            errors.append(f"transaction #{index}: {result.message}")

    if errors:
        return Error(errors)

    return Ok(total)


# ============================================================
# Демонстрація роботи
# ============================================================

if __name__ == "__main__":
    print("Завдання 1:")
    print("divide_with_try_except(10, 0) =", divide_with_try_except(10, 0))

    print("\nЗавдання 2:")
    print("safe_divide_tuple(10, 2) =", safe_divide_tuple(10, 2))
    print("safe_divide_tuple(10, 0) =", safe_divide_tuple(10, 0))

    print("\nЗавдання 4-6: Option")
    print("safe_divide_option(10, 2) =", safe_divide_option(10, 2))
    print("safe_divide_option(10, 0) =", safe_divide_option(10, 0))
    print("option_chain_example() =", option_chain_example())
    print("option_chain_error_example() =", option_chain_error_example())

    print("\nЗавдання 8-11: Result")
    print("safe_divide(10, 2) =", safe_divide(10, 2))
    print("safe_divide(10, 0) =", safe_divide(10, 0))
    print("safe_pipeline(10) =", safe_pipeline(10))

    print("\nЗавдання 12:")
    print('validate_user_age({"age": "25"}) =', validate_user_age({"age": "25"}))
    print('validate_user_age({"age": "17"}) =', validate_user_age({"age": "17"}))
    print('validate_user_age({"age": "abc"}) =', validate_user_age({"age": "abc"}))

    print("\nЗавдання 13:")
    print('read_file("hello.txt") =', read_file("hello.txt"))
    print('read_file("missing.txt") =', read_file("missing.txt"))

    print("\nЗавдання 14:")
    print('validate_user_all_errors({"name": "Alice", "age": 17}) =',
          validate_user_all_errors({"name": "Alice", "age": 17}))
    print('validate_user_all_errors({"name": "", "age": "abc"}) =',
          validate_user_all_errors({"name": "", "age": "abc"}))
    print('validate_user_all_errors({"name": "Alice", "age": 25}) =',
          validate_user_all_errors({"name": "Alice", "age": 25}))

    print("\nЗавдання 15:")
    print("sum_transactions(transactions) =", sum_transactions(transactions))
    print("sum_transactions(valid transactions) =",
          sum_transactions([{"amount": "100"}, {"amount": "200"}]))
