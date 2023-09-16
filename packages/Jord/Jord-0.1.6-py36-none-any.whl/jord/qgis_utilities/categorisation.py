import random
from itertools import cycle
from typing import Iterable, Sized, Callable, Generator

from PyQt5.Qt import QColor

# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsVectorLayer,
    QgsSymbol,
    QgsRendererCategory,
    QgsCategorizedSymbolRenderer,
)

from warg import TripleNumber, QuadNumber, n_uint_mix_generator_builder

__all__ = ["categorise_layer"]


def random_rgb(mix: TripleNumber = (255, 255, 255)) -> TripleNumber:
    red = random.randrange(0, mix[0])
    green = random.randrange(0, mix[1])
    blue = random.randrange(0, mix[2])
    return (red, green, blue)


def random_rgba(mix: QuadNumber = (1, 1, 1, 1)) -> QuadNumber:
    red = random.randrange(0, mix[0])
    green = random.randrange(0, mix[1])
    blue = random.randrange(0, mix[2])
    alpha = random.randrange(0, mix[3])
    return (red, green, blue, alpha)


def random_color_generator() -> TripleNumber:
    while 1:
        yield random_rgb()


def random_color_alpha_generator() -> QuadNumber:
    while 1:
        yield random_rgba()


def categorise_layer(
    layer: QgsVectorLayer,
    field_name: str = "layer",
    iterable: Iterable = n_uint_mix_generator_builder(255, 255, 255, 255),
) -> None:
    if isinstance(iterable, Sized):
        iterable = cycle(iterable)
    if isinstance(iterable, Callable) and not isinstance(iterable, Generator):
        iterable = iterable()  # Compat
    color_iter = iter(iterable)

    render_categories = []
    for cat in layer.uniqueValues(layer.fields().indexFromName(field_name)):
        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        col = next(color_iter)
        if len(col) == 3:
            col = (*col, 255)
        sym.setColor(QColor(*col))
        label = str(cat)
        render_categories.append(
            QgsRendererCategory(cat, symbol=sym, label=label, render=True)
        )

    layer.setRenderer(QgsCategorizedSymbolRenderer(field_name, render_categories))
    layer.triggerRepaint()
