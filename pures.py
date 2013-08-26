from peewee import *

database = SqliteDatabase('dev.db', **{})


class Compound(BaseModel):
    formula = CharField()
    formula_extended = TextField(null=True)
    name = CharField()

    pc = FloatField()
    tc = FloatField()
    vc = FloatField()

    weight = FloatField(null=True)

    a = FloatField(null=True)
    acentric_factor = FloatField(null=True)
    b = FloatField(null=True)
    c = FloatField(null=True)
    d = FloatField(null=True)

    class Meta:
        db_table = 'compound'
