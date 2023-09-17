from dataclasses import dataclass
from typing import Tuple, List

from PowerfulDiceRoller.models.DiceThrown import DiceThrown


@dataclass
class LarkThrown:
    raw: str
    total: int = None
    dices: List[Tuple[str, DiceThrown]] = None

    @property
    def total_formula(self) -> str:
        result = self.raw
        for dice, cls in self.dices:
            result = result.replace(dice, cls.to_str(view_strike=True, ), 1)
        return result + f"={self.total}"

    @property
    def replaced_dices(self) -> str:
        result = self.raw
        for dice, cls in self.dices:
            result = result.replace(dice, str(cls.total), 1)
        return result