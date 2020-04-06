from __future__ import absolute_import

from bitfield.types import Bit, BitHandler
from django.db.models.lookups import Exact


class BitQueryLookupWrapper(Exact):  # NOQA
    def process_lhs(self, qn, connection, lhs=None):
        lhs_sql, params = super(BitQueryLookupWrapper, self).process_lhs(
            qn, connection, lhs)
        if self.rhs:
            lhs_sql = lhs_sql + ' & %s'
        else:
            lhs_sql = lhs_sql + ' | %s'
        params.extend(self.get_db_prep_lookup(self.rhs, connection)[1])
        return lhs_sql, params

    def get_db_prep_lookup(self, value, connection, prepared=False):
        v = value.mask if isinstance(value, (BitHandler, Bit)) else value
        return super(BitQueryLookupWrapper, self).get_db_prep_lookup(v, connection)

    def get_prep_lookup(self):
        return self.rhs


class BitQuerySaveWrapper(BitQueryLookupWrapper):
    def as_sql(self, compiler, connection):
        """
        Create the proper SQL fragment. This inserts something like
        "(T0.flags & value) != 0".

        This will be called by Where.as_sql()
        """
        op = '|' if self.bit else '&~'
        qn = compiler.quote_name_unless_alias
        return ("%s.%s %s %d" % (qn(self.table_alias), qn(self.column), op, self.bit.mask), [])

    def as_oracle(self, compiler, connection):
        if not self.bit:
            qn = compiler.quote_name_unless_alias
            return ("%s.%s & (-(%d)-1)" % (qn(self.table_alias), qn(self.column), self.bit.mask), [])
        return self.as_sql(compiler, connection)
