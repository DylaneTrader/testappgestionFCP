#!/bin/bash
# Script de vérification de l'état de la base de données

echo "============================================================"
echo "VÉRIFICATION DE LA BASE DE DONNÉES FCP"
echo "============================================================"
echo ""

# Vérifier que la base de données existe
if [ -f "db.sqlite3" ]; then
    echo "✅ Base de données SQLite trouvée"
    SIZE=$(du -h db.sqlite3 | cut -f1)
    echo "   Taille: $SIZE"
else
    echo "❌ Base de données non trouvée"
    exit 1
fi

# Vérifier les modèles
echo ""
echo "Vérification des modèles Django..."
python manage.py check --deploy

# Afficher les statistiques
echo ""
echo "============================================================"
echo "STATISTIQUES DE LA BASE DE DONNÉES"
echo "============================================================"
python manage.py shell << 'EOF'
from fcp_app.models import *

print("\n📊 Données principales:")
print(f"  - FCPs: {FCP.objects.count()}")
print(f"  - Valeurs Liquidatives: {ValeurLiquidative.objects.count()}")
print(f"  - Souscriptions/Rachats: {SouscriptionRachat.objects.count()}")
print(f"  - Actifs Nets: {ActifNet.objects.count()}")
print(f"  - Compositions: {CompositionFCP.objects.count()}")
print(f"  - Benchmarks: {Benchmark.objects.count()}")
print(f"  - Poids Quotidiens: {PoidsQuotidien.objects.count()}")

print("\n📊 Données de référence:")
print(f"  - Types de clients: {TypeClient.objects.count()}")
print(f"  - Types d'opérations: {TypeOperation.objects.count()}")
print(f"  - Types de FCP: {TypeFCP.objects.count()}")
print(f"  - Classes d'actifs: {ClasseActif.objects.count()}")
print(f"  - Secteurs: {Secteur.objects.count()}")
print(f"  - Pays: {Pays.objects.count()}")

# Dernière date
from django.db.models import Max
derniere_vl = ValeurLiquidative.objects.aggregate(Max('date'))['date__max']
dernier_bench = Benchmark.objects.aggregate(Max('date'))['date__max']

print(f"\n📅 Dernières données:")
print(f"  - Dernière valeur liquidative: {derniere_vl}")
print(f"  - Dernier benchmark: {dernier_bench}")

print("\n✅ Base de données opérationnelle")
EOF

echo ""
echo "============================================================"
echo "✅ VÉRIFICATION TERMINÉE"
echo "============================================================"
