"""Проверки сырых данных ПРАЙМ (семинар 3).

Каждая функция принимает таблицу и возвращает ПЛОХИЕ строки.
Не число и не True/False, а именно строки: их можно открыть и посмотреть.
Пустой результат значит "дефекта нет", это тоже результат.
"""

import pandas as pd


def find_missing_channel(df: pd.DataFrame) -> pd.DataFrame:
    """Клиенты без канала привлечения.

    groupby и value_counts по умолчанию молча выбрасывают пропуски,
    поэтому таких клиентов надо искать отдельно.
    """
    return df[df["acquisition_channel"].isna()]


def find_reversed_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Сессии, которые кончились раньше, чем начались (ended_at < started_at)."""
    return df[df["ended_at"] < df["started_at"]]


def find_duplicate_payments(df: pd.DataFrame, gap_minutes: int = 20) -> pd.DataFrame:
    """Двойные списания: та же подписка, та же сумма, и между ними меньше gap_minutes.

    Почему не drop_duplicates: одна и та же сумма по подписке каждый месяц
    это нормальное продление, а не дубль. Дубль это БЛИЗОСТЬ во времени.
    Порог 20 минут взят с семинара 3: от 15 минут до суток ответ не меняется.
    """
    # Сортируем, чтобы платежи одной подписки и одной суммы шли подряд по времени.
    s = df.sort_values(["subscription_id", "amount", "paid_at"])
    # diff() внутри группы: сколько времени прошло с предыдущего такого же платежа.
    # У первого платежа группы предыдущего нет, там будет NaT, и сравнение даст False.
    gap = s.groupby(["subscription_id", "amount"])["paid_at"].diff()
    return s[gap < pd.Timedelta(minutes=gap_minutes)]


def find_nonpositive_amounts(df: pd.DataFrame) -> pd.DataFrame:
    """Покупки с невозможной суммой: ноль или меньше нуля.

    Знак <= важен: со знаком < нулевые суммы не попали бы в проверку.
    """
    return df[df["amount"] <= 0]
