# rolling_dice

This is the library for python3.7+ for getting result if throwable dices by human notations.  

Powered by Lark

## Example  

2d20 - get sum in throw 20-sided dice 2 times.

## Install

> pip install rolling-dice

## How to use

```
from rolling_dice import get_result

...

result = get_result("4d6+1")[0] # List[Result]

print(result.total) # 12
print(result.replaced_dices) # "11+1"
print(result.total_formula) # "[2+5+1+3]+1=12"
```

### Dice notation

- {dice} as {throws}[dkdc]{faces}, where:
- - {throws} - how many random results to get;  
- - [dkdk] - one of the delimiters listed;
- - {faces} - the number of faces of the dice to throw.  
- To highlight the [number] larger or smaller roll results, use {dice}[hв]{number} or {roll}[lн]{number} respectively.
- To repeat multiple [times] identical rolls, use [times]x[throws] or [throws]x[times]
- Supports the following arithmetic operations on dice and numbers "+", "-", "*", "/".
- Аnd also prioritizes actions, when using round and square brackets "((", ")", "[", "]"" 

### Examples

```
"d20"
"(2d20)d20"
"2+2*2"
"3к6в2+1"
"d6+d6+d6+d6"
"6x3к6в2+1"
"4к6+1"
"4к1в3+1"
"6х4к6в3+1"
"100000d1000"
```