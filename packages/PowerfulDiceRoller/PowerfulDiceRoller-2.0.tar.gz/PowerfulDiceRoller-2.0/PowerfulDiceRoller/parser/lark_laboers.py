from operator import add, mul, sub, truediv as div
from typing import Union

from lark import Tree, Lark

from PowerfulDiceRoller.models.DiceThrown import DiceThrown


def simple_calculation(tree: Tree) -> int:
    values = [get_next_point(child) for child in tree.children]
    if tree.data == "add":
        return add(*values)
    elif tree.data == "sub":
        return sub(*values)
    elif tree.data == "mul":
        return mul(*values)
    elif tree.data == "div":
        return div(*values)


def parse_roll_dice(tree: Tree) -> DiceThrown:
    if len(tree.children) == 2:
        thrown, face = [get_next_point(child) for child in tree.children]
    else:
        thrown, face = 1, get_next_point(*tree.children)
    return DiceThrown(times=thrown, faces=face)


def filtration_dices(tree: Tree) -> DiceThrown:
    dice: DiceThrown = get_next_point(tree.children[0])

    if tree.data == "max":
        dice._amount_function = max
    elif tree.data == "min":
        dice._amount_function = min
    dice._amount_rate = get_next_point(tree.children[1]) if len(tree.children) > 1 else 1
    return dice


def get_next_point(tree: Tree) -> Union[int, DiceThrown, Tree]:
    if tree.data in ("add", "sub", "mul", "div"):
        return simple_calculation(tree)
    elif tree.data == "to_int":
        return int(tree.children[0])
    elif tree.data == "res":
        return sum([get_next_point(child) for child in tree.children])
    elif tree.data == "dice":
        return parse_roll_dice(tree)
    elif tree.data in ("max", "min"):
        return filtration_dices(tree)


def open_lark(text, grammar):
    return get_next_point(Lark(grammar, start="start").parse(text))