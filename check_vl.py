import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionFCP.settings')
django.setup()

from fcp_app.models import FicheSignaletique, ValeurLiquidative
from django.db.models import Min, Max, Count

print('=== Statistiques VL ===')
print(f'Total: {ValeurLiquidative.objects.count()} valeurs liquidatives')

stats = ValeurLiquidative.objects.aggregate(date_min=Min('date'), date_max=Max('date'))
print(f"Periode: {stats['date_min']} a {stats['date_max']}")

print('')
print('=== VL par FCP ===')
for fcp in FicheSignaletique.objects.annotate(vl_count=Count('valeurs_liquidatives')):
    print(f'  {fcp.nom}: {fcp.vl_count} VL')
