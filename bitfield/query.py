from django.db.models.lookups import Exact


class BitQueryLookupWrapper(Exact):

    def process_lhs(self, qn, connection, lhs=None):
        lhs_sql, params = super(BitQueryLookupWrapper, self).process_lhs(
            qn, connection, lhs)
        lhs_sql = lhs_sql + ' & %s'
        params.extend(self.get_db_prep_lookup(self.rhs, connection)[1])
        return lhs_sql, params


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
