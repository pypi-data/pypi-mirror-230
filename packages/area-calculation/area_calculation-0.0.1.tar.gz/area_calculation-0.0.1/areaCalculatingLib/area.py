import math
from typing import Union


def find_area(radius: Union[int, float, None] = None,
              a: Union[int, float, None] = None,
              b: Union[int, float, None] = None,
              c: Union[int, float, None] = None) -> Union[float, int, str]:
    if radius is not None and not all([a, b, c]):
        if not isinstance(radius, int):
            return "Некорректные данные"
        return circle_area(radius)
    if all([a, b, c]) and radius is None:
        if not type_checking([a, b, c]):
            return "Некорректные данные"
        return triangle_area(a, b, c)
    if all([radius, a, b, c]):
        if not type_checking([radius, a, b, c]):
            return "Некорректные данные"
        return f"{circle_area(radius)}, {triangle_area(a, b, c)}"
    return "Некорректные данные"


def triangle_area(a: int, b: int, c: int) -> Union[float, int, str]:
    if a <= 0 or b <= 0 or c <= 0:
        return "Некорректные данные"
    if a + b < c or a + c < b or b + c < a:
        return "Некорректные данные"
    if a ** 2 + b ** 2 == c ** 2 or a ** 2 + c ** 2 == b ** 2 or b ** 2 + c ** 2 == a ** 2:
        print("Треугольник прямоугольный")
    p: float = (a + b + c) / 2
    return round(math.sqrt(p * (p - a) * (p - b) * (p - c)), 5)


def circle_area(radius: int) -> Union[float, int, str]:
    if radius <= 0:
        return "Некорректные данные"
    return round(math.pi * (radius ** 2), 5)


def type_checking(values: list[Union[float, int]]) -> bool:
    for value in values:
        if not isinstance(value, (int, float)):
            return False
    return True
