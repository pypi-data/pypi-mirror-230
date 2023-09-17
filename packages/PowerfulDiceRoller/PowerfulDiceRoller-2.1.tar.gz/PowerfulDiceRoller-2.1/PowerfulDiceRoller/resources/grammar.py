GRAMMAR_CALCULATOR = """\
?start      : s_math

?s_math     : s_math "+" s_math         -> add
            | s_math "-" s_math         -> sub
            | h_math

?h_math     : h_math "*" h_math         -> mul
            | h_math "/" h_math         -> div
            | result
            | num

?result     : num                -> res

?num        : "(" s_math ")"
            | "[" s_math "]"
            | NUMBER                    -> to_int

%import common.NUMBER
%ignore " "
"""

GRAMMAR_DICE = """\
?start      : filtration
?filtration : filtration "h" num? -> max
            | filtration "в" num? -> max
            | filtration "l" num? -> min
            | filtration "н" num? -> min
            | dice
?dice       : num? "d" num        -> dice
            | num? "к" num        -> dice
            | num? "k" num        -> dice
            | num? "д" num        -> dice
?num        : NUMBER              -> to_int
%import common.NUMBER
%ignore " "
"""