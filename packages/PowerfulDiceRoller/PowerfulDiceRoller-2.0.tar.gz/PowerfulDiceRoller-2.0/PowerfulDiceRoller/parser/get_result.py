from re import search, findall
from typing import List

from PowerfulDiceRoller.models.DiceThrown import DiceThrown
from PowerfulDiceRoller.models.LarkThrown import LarkThrown
from PowerfulDiceRoller.models.errors.ParseError import ParseError
from PowerfulDiceRoller.parser.lark_laboers import open_lark
from PowerfulDiceRoller.resources import GRAMMAR_DICE, GRAMMAR_CALCULATOR


def get_result(text,
               grammar_dice=GRAMMAR_DICE,
               grammar_calc=GRAMMAR_CALCULATOR) -> List:
    results = []
    for recursion in findall(r"\(([^\(\)]+)\)", text):
        text = text.replace(f"({recursion})",
                            str(sum(el.total for el in get_result(recursion, grammar_dice=grammar_dice, grammar_calc=grammar_calc))))
    repeats_math = search(r"(^\d+)[хx]|[хx](\d+$)", text)
    repeats = repeats_math.group(1) or repeats_math.group(2) if repeats_math else 1
    for _ in range(int(repeats) if int(repeats) < 10 else 10):
        t = text.replace(repeats_math.group(0), "") if repeats_math else text
        result = LarkThrown(raw=t)
        result.dices = []
        for dice in findall(r"(\d*[dkдк]\d+[hlвнd]?\d*)", t):
            value: DiceThrown = open_lark(text=dice, grammar=grammar_dice)
            result.dices.append((dice, value))
        result.total = open_lark(text=result.replaced_dices, grammar=grammar_calc)
        if str(result.total) == t:
            raise ParseError
        results.append(result)
    return results
