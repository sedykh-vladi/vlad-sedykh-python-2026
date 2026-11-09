"""Факторное разложение и каскадная диаграмма (лекция 6, семинар 6).

Главное правило: сумма влияний факторов равна изменению показателя.
Каждая функция проверяет это через assert. Не сошлось, значит что-то потеряли,
и код упадёт сразу, а не в отчёте.
"""

import math

import matplotlib.pyplot as plt
import pandas as pd


def chain(n0, p0, n1, p1):
    """Цепные подстановки для показателя R = N x P (два фактора).

    n0, p0 значения "было", n1, p1 значения "стало".
    Порядок курса: сначала количество ("сколько"), потом цена ("почём").
    Возвращает два числа в рублях: (влияние количества, влияние цены).
    """
    # Шаг 1. Меняем только количество, цена ещё старая.
    by_count = (n1 - n0) * p0
    # Шаг 2. Меняем цену, а количество уже новое.
    # Поэтому совместный член (n1 - n0) * (p1 - p0) достаётся цене: она идёт второй.
    by_price = n1 * (p1 - p0)
    # Проверка: два влияния в сумме дают всё изменение. Допуск 1 копейка из-за float.
    assert abs(by_count + by_price - (n1 * p1 - n0 * p0)) < 0.01, "сумма влияний не равна изменению"
    return round(by_count), round(by_price)


def contrib(x0: dict, x1: dict, order: list[str]) -> dict:
    """Цепные подстановки для любого числа множителей: R = x_1 * x_2 * ... * x_k.

    x0 словарь "было" (фактор -> значение), x1 словарь "стало".
    order порядок, в котором факторы переходят со старого значения на новое.
    Возвращает словарь: фактор -> его влияние в рублях.
    """
    cur = dict(x0)  # копия "было": её будем менять по одному фактору
    out = {}
    for f in order:
        before = math.prod(cur.values())  # показатель до шага
        cur[f] = x1[f]  # этот фактор стал новым, остальные стоят на месте
        out[f] = math.prod(cur.values()) - before  # насколько изменился показатель на этом шаге
    total = math.prod(x1.values()) - math.prod(x0.values())
    assert abs(sum(out.values()) - total) < 0.01, "сумма влияний не равна изменению"
    return out


def waterfall(deltas: pd.Series, title: str, total_label: str = "итого") -> plt.Axes:
    """Каскад изменений: по столбику на фактор и итоговый столбик в конце.

    deltas влияния факторов (индекс это подписи столбиков, значения это высоты).
    title заголовок графика, в нём пишем ВЫВОД, а не название.
    """
    # Где начинается каждый столбик: там, где закончился предыдущий.
    # cumsum копит сумму, минус сам столбик даёт уровень ДО него.
    before = deltas.cumsum() - deltas
    # Цвет по знаку: падение красное, рост зелёный.
    colors = ["#C1272D" if v < 0 else "#2A9D8F" for v in deltas]

    fig, ax = plt.subplots(figsize=(9, 4.6), layout="constrained")
    # Главная строка каскада: bottom задаёт нижний уровень столбика.
    bars = ax.bar(deltas.index, deltas, bottom=before, color=colors, zorder=2)
    # Итог стоит на нуле, серым: это не фактор, а результат.
    total = ax.bar(total_label, deltas.sum(), color="#6B7280", zorder=2)
    for group in (bars, total):
        # Подписи со знаком и пробелом в тысячах: +1 234 или -1 234.
        ax.bar_label(group, fmt=lambda v: f"{v:+,.0f}".replace(",", " "), padding=3)
    ax.axhline(0, color="#111827", linewidth=0.8)  # линия нуля: ось столбиков включает ноль
    ax.set_title(title, loc="left")
    ax.use_sticky_edges = False  # иначе подписи упрутся в край графика
    ax.margins(y=0.15)
    ax.spines[["top", "right"]].set_visible(False)  # лишние рамки убираем
    ax.grid(axis="y", color="#E5E7EB")
    return ax
