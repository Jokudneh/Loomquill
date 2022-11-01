from flyteidl.core import condition_pb2 as _condition

from flytekit.models import common as _common
from flytekit.models import literals as _literals


class ComparisonExpression(_common.FlyteIdlEntity):
    class Operator(object):
        """
        Binary Operator for each expression
        """

        EQ = _condition.ComparisonExpression.EQ
        NEQ = _condition.ComparisonExpression.NEQ
        GT = _condition.ComparisonExpression.GT
        GTE = _condition.ComparisonExpression.GTE
        LT = _condition.ComparisonExpression.LT
        LTE = _condition.ComparisonExpression.LTE

    def __init__(self, operator, left_value, right_value):
        """
        Defines a 2-level tree where the root is a comparison operator and Operands are primitives or known variables.
        Each expression results in a boolean result.

        :param Operator operator:
        :param Operand left_value:
        :param Operand right_value:
        """
        self._operator = operator
        self._left_value = left_value
        self._right_value = right_value

    @property
    def operator(self):
        """
        Gets the operator representing this comparison expression.
        :rtype: ComparisonExpression.Operator
        """
        return self._operator

    @property
    def left_value(self):
        """
        Gets the left value for the comparison expression.
        :rtype: Operand
        """
        return self._left_value

    @property
    def right_value(self):
        """
        Gets the right value for the comparison expression.
        :rtype: Operand
        """
        return self._right_value

    def to_flyte_idl(self):
        """
        :rtype: flyteidl.core.condition_pb2.ComparisonExpression
        """
        return _condition.ComparisonExpression(
            operator=self.operator,
            left_value=self.left_value.to_flyte_idl(),
            right_value=self.right_value.to_flyte_idl(),
        )

    @classmethod
