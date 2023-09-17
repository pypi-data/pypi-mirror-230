import typing

from PowerfulDiceRoller.models.Dice import Dice
from PowerfulDiceRoller.models.errors.DiceError import DiceError


class DiceThrown:
    __slots__ = ("_times",
                 "_face",
                 "_amount_function",
                 "_amount_rate",
                 "_result",
                 "_amount",
                 "_dices",
                 )

    def __init__(self,
                 times: int,
                 faces: int,
                 dropout_function: typing.Callable = None,
                 dropout_rate: int = None) -> None:
        self._times = times
        self._face = faces
        self._amount_function = dropout_function
        self._amount_rate = dropout_rate

        self._amount = None

        self._dices: typing.List[Dice] = [Dice(face=faces) for _ in range(self._times)]

        if any((dropout_function, dropout_rate)) and not all((dropout_rate, dropout_function)):
            raise DiceError

    def to_str(self, view_strike=False, startswith_strike='<strike>', endswith_strike='</strike>') -> str:
        values = list(map(str, self.dices))
        if view_strike:
            amount = self.amount.copy()
            for i, dice in enumerate(self.dices):
                if dice in amount:
                    amount.remove(dice)
                else:
                    values[i] = f"{startswith_strike}{dice.result}{endswith_strike}"
        return f"[{'+'.join(values)}]"

    def __repr__(self) -> str:
        return f"DiceThrown(throw={self.times}, face={self.face}, amount_function = {self._amount_function}, " \
               f"amount_rate = {self._amount_rate}, result = {self.total})"

    def _get_amount(self) -> typing.Optional[typing.List[Dice]]:
        if self._amount_function is None and self._amount_rate is None:
            return self._dices
        if any((self._amount_function, self._amount_rate)) and not all((self._amount_function, self._amount_rate)):
            raise DiceError("Unspecified retain formula or count for save")
        elif self._amount_rate > self._times:
            return self._dices
        dices = self._dices.copy()
        results = []
        for _ in range(self._amount_rate):
            exclude = self._amount_function(dices)
            dices.remove(exclude)
            results.append(exclude)
        return results

    @property
    def times(self) -> int:
        return self._times

    @property
    def face(self) -> int:
        return self._face

    @property
    def amount(self) -> typing.Optional[typing.List[Dice]]:
        if self._amount_function is None and self._amount_rate is None:
            return self.dices
        if self._amount is None:
            self._amount = self._get_amount()
        return self._amount

    @property
    def total(self) -> int:
        if self.amount:
            return sum(self.amount)
        return sum(self._dices)

    @property
    def dices(self) -> typing.List[Dice]:
        return self._dices
