import json
from django.core import serializers
from sur.models import (Compound, K0InteractionParameter,
                        KijInteractionParameter,
                        LijInteractionParameter,
                        TstarInteractionParameter)


def dump_json(json_path, indent=2):
    """
    A helper function to dump models from the current database state.
    Useful to update data/initial_data.json

    it's analog to

        manage.py dumpdata --indent=2 sur.Compound sur.K0InteractionParameter sur.KijInteractionParameter sur.LijInteractionParameter sur.TstarInteractionParameter > json_path

    but taking care of current in memory saved data.
    """




    l = []
    for m in (Compound, K0InteractionParameter, KijInteractionParameter, LijInteractionParameter, TstarInteractionParameter):
        l.extend(json.loads(serializers.serialize("json", m.objects.all())))
    json.dump(l, open(json_path, 'w'), indent=indent)