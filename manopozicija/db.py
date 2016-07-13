from django.db.models import Func
from django.db.models import FloatField


class Similarity(Func):
    function = 'SIMILARITY'

    def __init__(self, *expressions, **extra):
        extra.setdefault('output_field', FloatField())
        super().__init__(*expressions, **extra)
