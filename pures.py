from peewee import *

db = SqliteDatabase('dev.db', **{})


class Compound(Model):
    name = CharField(unique=True)
    formula = CharField()
    formula_extended = CharField(null=True)
    pc = FloatField()
    tc = FloatField()
    vc = FloatField()
    acentric_factor = FloatField(null=True)
    weight = FloatField(null=True)
    a = FloatField(null=True)
    b = FloatField(null=True)
    c = FloatField(null=True)
    d = FloatField(null=True)


    def __unicode__(self):
        return self.name

    class Meta:
        database = db
        db_table = 'compound'


class Alias(Model):
    compound = ForeignKeyField(Compound, related_name='alias')
    alias = CharField(unique=True)

