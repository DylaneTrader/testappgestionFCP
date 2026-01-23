import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionFCP.settings')
django.setup()

from fcp_app.models import FicheSignaletique, FCP_VL_MODELS
from django.db.models import Min, Max

print('=== Statistiques VL ===')
total_vl = 0
date_min = None
date_max = None

for nom_fcp, model_vl in FCP_VL_MODELS.items():
    count = model_vl.objects.count()
    total_vl += count
    
    if count > 0:
        stats = model_vl.objects.aggregate(d_min=Min('date'), d_max=Max('date'))
        if date_min is None or (stats['d_min'] and stats['d_min'] < date_min):
            date_min = stats['d_min']
        if date_max is None or (stats['d_max'] and stats['d_max'] > date_max):
            date_max = stats['d_max']

print(f'Total: {total_vl} valeurs liquidatives')
print(f'Periode: {date_min} a {date_max}')

print('')
print('=== VL par FCP ===')
for nom_fcp, model_vl in FCP_VL_MODELS.items():
    count = model_vl.objects.count()
    print(f'  {nom_fcp}: {count} VL')

print('')
print('=== FCP en base ===')
print(f'Total FicheSignaletique: {FicheSignaletique.objects.count()}')
