import dataclasses
import random

from PowerfulDiceRoller.models.errors import NegativeDiceFaces


@dataclasses.dataclass
class Dice:
    __slots__ = ("_face", "__result")

    def __init__(self, face: int):
        if not isinstance(face, int):
            raise TypeError(f"Face type must be {type(int)}, not {type(face)}")
        elif not face > 0:
            raise NegativeDiceFaces(f"Face value must be >= 1, not {face}")
        self._face: int = face
        self.__result: int = random.randint(1, self._face)

    @property
    def face(self) -> int:
        return self._face

    @property
    def result(self) -> int:
        return self.__result

    def set_result(self, num: int) -> None:
        self.__result = num

    def __int__(self) -> int:
        return self.result

    def __str__(self) -> str:
        return str(self.result)

    def __repr__(self) -> str:
        return f"Dice(face={self._face}, __result={self.result})"

    def __add__(self, other) -> int:  # +
        if isinstance(other, type(self)):
            return self.result + other.result
        return self.result + other

    def __sub__(self, other):  # -
        if isinstance(other, type(self)):
            return self.result - other.result
        return self.result - other

    def __mul__(self, other):  # *
        if isinstance(other, type(self)):
            return self.result * other.result
        return self.result * other

    def __truediv__(self, other):  # /
        if isinstance(other, type(self)):
            return self.result / other.result
        return self.result / other

    def __floordiv__(self, other):  # //
        if isinstance(other, type(self)):
            return self.result // other.result
        return self.result // other

    def __radd__(self, other) -> int:
        return other + self.result

    def __rsub__(self, other):
        return other - self.result

    def __rmul__(self, other):
        return other * self.result

    def __rtruediv__(self, other):
        return other / self.result

    def __rfloordiv__(self, other):
        return other // self.result

    def __eq__(self, other):  # ==
        if isinstance(other, type(self)):
            return self.result == other.result

        return self.result == other

    def __lt__(self, other):  # <=
        if isinstance(other, type(self)):
            return self.result < other.result
        return self.result < other