__all__ = ('bitand', 'bitor')

try:
    from django.db.models.expressions import ExpressionNode
    ExpressionNode.BITAND  # noqa
    del ExpressionNode
except AttributeError:
    # Django < 1.5
    def bitand(a, b):
        return a & b

    def bitor(a, b):
        return a | b
else:
    def bitand(a, b):
        return a.bitand(b)

    def bitor(a, b):
        return a.bitor(b)
