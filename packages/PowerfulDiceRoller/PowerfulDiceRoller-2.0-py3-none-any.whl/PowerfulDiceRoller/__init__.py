import sys

if sys.version_info < (3, 7):
    raise ImportError('Your Python version {0} is not supported by dice_roll, please install '
                      'Python 3.7+'.format('.'.join(map(str, sys.version_info[:3]))))

from PowerfulDiceRoller.models import (Dice,
                                       DiceThrown,
                                       LarkThrown,
                                       DiceError,
                                       NotFoundMethod,
                                       ParseError,
                                       NegativeDiceFaces)
from PowerfulDiceRoller.parser import get_result, open_lark
from PowerfulDiceRoller.resources import GRAMMAR_CALCULATOR, GRAMMAR_DICE

__all__ = (
    "Dice",
    "DiceThrown",
    "LarkThrown",
    "DiceError",
    "NotFoundMethod",
    "ParseError",
    "get_result",
    "open_lark",
    "GRAMMAR_CALCULATOR",
    "GRAMMAR_DICE"
)

__version__ = '2.0'
