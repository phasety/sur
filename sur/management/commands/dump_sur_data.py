from optparse import make_option
import sys
from django.core.management.base import BaseCommand
from django.core import serializers
import json
from sur.models import (Compound, K0InteractionParameter,
                        KijInteractionParameter,
                        LijInteractionParameter,
                        TstarInteractionParameter)



class Command(BaseCommand):
    help = """Dump a json with the current Sur's database. Useful to update data/initial_data.json"""

    option_list = BaseCommand.option_list + (
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('-o', '--output', default=None, dest='output',
            help='Specifies file to which the output is written.'))

    def handle(self, *args, **options):
        indent = options.get('indent')
        output = options.get('output')

        stream = open(output, 'w') if output else sys.stdout
        l = []
        for m in (Compound, K0InteractionParameter, KijInteractionParameter, LijInteractionParameter, TstarInteractionParameter):
            l.extend(json.loads(serializers.serialize("json", m.objects.all())))
        json.dump(l, stream, indent=indent)

