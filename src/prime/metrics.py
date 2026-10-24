"""Метрики подписки ПРАЙМ.

revenue() осталась со второго семинара: она работает со списком словарей.
Функции ниже работают с pandas (семинар 5).
"""

import pandas as pd


def revenue(payments: list[dict]) -> float:
    """Выручка: сумма списаний."""
    return sum(p["amount"] for p in payments)


def active_on(subs: pd.DataFrame, moment: pd.Timestamp) -> pd.Series:
    """Маска подписок, активных в момент moment.

    Активна = началась раньше moment И (ещё не закончилась ИЛИ закончилась не раньше moment).
    Пустой ended_at штатный: подписка действует.
    """
    return (subs["started_at"] < moment) & (subs["ended_at"].isna() | (subs["ended_at"] >= moment))


def churn_rate(subs: pd.DataFrame, start: str, end: str) -> float:
    """Отток за период [start, end): доля подписок, активных на start, которые закончились до end.

    Знаменатель: только активные на НАЧАЛО периода. Подписки, оформленные внутри
    периода, не берём: иначе отток зависел бы от того, сколько продали в этом месяце.
    Даты переводим в UTC: в базе всё время хранится в UTC.
    """
    start, end = pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
    active = subs[active_on(subs, start)]
    return (active["ended_at"] < end).sum() / len(active)
