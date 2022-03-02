from __future__ import absolute_import

from bitfield.types import Bit, BitHandler
from django.db.models.lookups import Exact


class BitQueryLookupWrapper(Exact):  # NOQA
    def process_lhs(self, compiler, connection, lhs=None):
        lhs_sql, lhs_params = super(BitQueryLookupWrapper, self).process_lhs(
            compiler, connection, lhs)

        if not isinstance(self.rhs, (BitHandler, Bit)):
            return lhs_sql, lhs_params

        op = ' & ' if self.rhs else ' | '
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        params = list(lhs_params)
        params.extend(rhs_params)

        return op.join((lhs_sql, rhs_sql)), params

    def get_db_prep_lookup(self, value, connection):
        v = value.mask if isinstance(value, (BitHandler, Bit)) else value
        return super(BitQueryLookupWrapper, self).get_db_prep_lookup(v, connection)

    def get_prep_lookup(self):
        if isinstance(self.rhs, (BitHandler, Bit)):
            return self.rhs  # resolve at later stage, in get_db_prep_lookup
        return super(BitQueryLookupWrapper, self).get_prep_lookup()


class BitQuerySaveWrapper(BitQueryLookupWrapper):
    def as_sql(self, qn, connection):
        """
        Create the proper SQL fragment. This inserts something like
        "(T0.flags & value) != 0".

        This will be called by Where.as_sql()
        """
        engine = connection.settings_dict['ENGINE'].rsplit('.', -1)[-1]
        if engine.startswith('postgres'):
            XOR_OPERATOR = '#'
        elif engine.startswith('sqlite'):
            raise NotImplementedError
        else:
            XOR_OPERATOR = '^'

        if self.bit:
            return ("%s.%s | %d" % (qn(self.table_alias), qn(self.column), self.bit.mask),
                    [])
        return ("%s.%s %s %d" % (qn(self.table_alias), qn(self.column), XOR_OPERATOR, self.bit.mask),
                [])
