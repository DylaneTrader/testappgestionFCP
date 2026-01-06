"""
Exemples de requêtes courantes pour la base de données FCP
"""
from fcp_app.models import *
from django.db.models import Sum, Avg, Max, Min, Count, Q, F
from datetime import datetime, timedelta


# ============================================================
# 1. REQUÊTES SUR LES FCPs
# ============================================================

# Obtenir tous les FCPs actifs
fcps_actifs = FCP.objects.filter(actif=True)

# Obtenir un FCP spécifique
fcp = FCP.objects.get(nom="FCP ACTIONS PHARMACIE")

# Compter le nombre de FCPs
nombre_fcps = FCP.objects.count()


# ============================================================
# 2. VALEURS LIQUIDATIVES
# ============================================================

# Dernière valeur liquidative d'un FCP
derniere_vl = ValeurLiquidative.objects.filter(
    fcp=fcp
).order_by('-date').first()

# Toutes les VL d'un FCP pour une année
vl_2024 = ValeurLiquidative.objects.filter(
    fcp=fcp,
    date__year=2024
).order_by('date')

# VL entre deux dates
from datetime import date
vl_periode = ValeurLiquidative.objects.filter(
    fcp=fcp,
    date__range=['2024-01-01', '2024-12-31']
)

# Statistiques sur les VL d'un FCP
stats_vl = ValeurLiquidative.objects.filter(fcp=fcp).aggregate(
    max_vl=Max('valeur'),
    min_vl=Min('valeur'),
    avg_vl=Avg('valeur'),
    count=Count('id')
)

# Évolution de la VL (calcul de performance)
vl_debut = ValeurLiquidative.objects.filter(
    fcp=fcp, date__year=2024
).order_by('date').first()

vl_fin = ValeurLiquidative.objects.filter(
    fcp=fcp, date__year=2024
).order_by('-date').first()

if vl_debut and vl_fin and vl_debut.valeur:
    performance = ((vl_fin.valeur - vl_debut.valeur) / vl_debut.valeur) * 100
    print(f"Performance 2024: {performance:.2f}%")


# ============================================================
# 3. SOUSCRIPTIONS ET RACHATS
# ============================================================

# Toutes les souscriptions d'un FCP
souscriptions = SouscriptionRachat.objects.filter(
    fcp=fcp,
    type_operation__nom="Souscriptions"
)

# Total des souscriptions
total_souscriptions = souscriptions.aggregate(Sum('montant'))['montant__sum']

# Rachats d'un FCP
rachats = SouscriptionRachat.objects.filter(
    fcp=fcp,
    type_operation__nom="Rachats"
)

# Solde net (Souscriptions - Rachats)
solde_net = total_souscriptions - rachats.aggregate(Sum('montant'))['montant__sum']

# Opérations par type de client
ops_par_client = SouscriptionRachat.objects.filter(fcp=fcp).values(
    'type_client__nom'
).annotate(
    total=Sum('montant'),
    nombre=Count('id')
).order_by('-total')

# Opérations récentes (30 derniers jours)
date_limite = date.today() - timedelta(days=30)
ops_recentes = SouscriptionRachat.objects.filter(
    fcp=fcp,
    date__gte=date_limite
).order_by('-date')

# Volume mensuel des opérations
from django.db.models.functions import TruncMonth
volume_mensuel = SouscriptionRachat.objects.filter(
    fcp=fcp,
    date__year=2024
).annotate(
    mois=TruncMonth('date')
).values('mois', 'type_operation__nom').annotate(
    total=Sum('montant'),
    nombre=Count('id')
).order_by('mois')


# ============================================================
# 4. ACTIFS NETS
# ============================================================

# Dernier actif net d'un FCP
dernier_actif = ActifNet.objects.filter(fcp=fcp).order_by('-date').first()

# Évolution de l'actif net sur l'année
actifs_2024 = ActifNet.objects.filter(
    fcp=fcp,
    date__year=2024
).order_by('date')

# Actif net moyen
actif_moyen = ActifNet.objects.filter(fcp=fcp).aggregate(Avg('montant'))

# Variation de l'actif net
actif_debut = ActifNet.objects.filter(
    fcp=fcp, date__year=2024
).order_by('date').first()

actif_fin = ActifNet.objects.filter(
    fcp=fcp, date__year=2024
).order_by('-date').first()

if actif_debut and actif_fin:
    variation = actif_fin.montant - actif_debut.montant
    variation_pct = (variation / actif_debut.montant) * 100
    print(f"Variation actif net 2024: {variation:,.2f} ({variation_pct:.2f}%)")


# ============================================================
# 5. COMPOSITION DES FCPs
# ============================================================

# Composition d'un FCP
composition = CompositionFCP.objects.filter(fcp=fcp).select_related(
    'type_fcp', 'classe', 'secteur', 'pays'
)

# Répartition par classe d'actif
repartition_classe = CompositionFCP.objects.filter(fcp=fcp).values(
    'classe__nom'
).annotate(
    total_pct=Sum('pourcentage')
).order_by('-total_pct')

# Répartition par secteur
repartition_secteur = CompositionFCP.objects.filter(fcp=fcp).values(
    'secteur__nom'
).annotate(
    total_pct=Sum('pourcentage')
).order_by('-total_pct')

# Répartition par pays
repartition_pays = CompositionFCP.objects.filter(fcp=fcp).values(
    'pays__nom'
).annotate(
    total_pct=Sum('pourcentage')
).order_by('-total_pct')

# Actifs cotés vs non cotés
repartition_cotation = CompositionFCP.objects.filter(fcp=fcp).values(
    'cotation__nom'
).annotate(
    total_pct=Sum('pourcentage')
)


# ============================================================
# 6. POIDS QUOTIDIENS
# ============================================================

# Dernier poids d'un FCP
dernier_poids = PoidsQuotidien.objects.filter(fcp=fcp).order_by('-date').first()

# Évolution des poids sur une période
poids_2024 = PoidsQuotidien.objects.filter(
    fcp=fcp,
    date__year=2024
).order_by('date')

# Poids moyen par classe d'actif
poids_moyens = PoidsQuotidien.objects.filter(fcp=fcp).aggregate(
    avg_actions=Avg('actions'),
    avg_obligations=Avg('obligations'),
    avg_opcvm=Avg('opcvm'),
    avg_liquidites=Avg('liquidites')
)


# ============================================================
# 7. BENCHMARKS
# ============================================================

# Dernier benchmark
dernier_benchmark = Benchmark.objects.order_by('-date').first()

# Benchmarks pour une année
benchmarks_2024 = Benchmark.objects.filter(date__year=2024).order_by('date')

# Performance du benchmark
bench_debut = Benchmark.objects.filter(date__year=2024).order_by('date').first()
bench_fin = Benchmark.objects.filter(date__year=2024).order_by('-date').first()

if bench_debut and bench_fin:
    perf_oblig = ((bench_fin.benchmark_obligataire - bench_debut.benchmark_obligataire) 
                  / bench_debut.benchmark_obligataire) * 100
    perf_actions = ((bench_fin.benchmark_actions - bench_debut.benchmark_actions) 
                    / bench_debut.benchmark_actions) * 100
    
    print(f"Performance benchmark obligataire 2024: {perf_oblig:.2f}%")
    print(f"Performance benchmark actions 2024: {perf_actions:.2f}%")


# ============================================================
# 8. REQUÊTES COMPLEXES
# ============================================================

# Top 5 des FCPs par actif net
top_fcps_actif = ActifNet.objects.filter(
    date=ActifNet.objects.latest('date').date
).select_related('fcp').order_by('-montant')[:5]

# FCPs avec le plus d'opérations
top_fcps_operations = SouscriptionRachat.objects.values(
    'fcp__nom'
).annotate(
    nb_ops=Count('id'),
    total_montant=Sum('montant')
).order_by('-nb_ops')[:10]

# Comparaison de performance entre FCPs
def comparer_performances(date_debut, date_fin):
    """Compare les performances de tous les FCPs sur une période"""
    fcps = FCP.objects.filter(actif=True)
    performances = []
    
    for fcp in fcps:
        vl_debut = ValeurLiquidative.objects.filter(
            fcp=fcp, date=date_debut
        ).first()
        vl_fin = ValeurLiquidative.objects.filter(
            fcp=fcp, date=date_fin
        ).first()
        
        if vl_debut and vl_fin and vl_debut.valeur:
            perf = ((vl_fin.valeur - vl_debut.valeur) / vl_debut.valeur) * 100
            performances.append({
                'fcp': fcp.nom,
                'performance': perf,
                'vl_debut': vl_debut.valeur,
                'vl_fin': vl_fin.valeur
            })
    
    return sorted(performances, key=lambda x: x['performance'], reverse=True)

# Analyse des flux nets par FCP
def analyser_flux_nets(annee=2024):
    """Analyse les flux nets (souscriptions - rachats) par FCP"""
    fcps = FCP.objects.filter(actif=True)
    resultats = []
    
    for fcp in fcps:
        souscriptions = SouscriptionRachat.objects.filter(
            fcp=fcp,
            date__year=annee,
            type_operation__nom="Souscriptions"
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        rachats = SouscriptionRachat.objects.filter(
            fcp=fcp,
            date__year=annee,
            type_operation__nom="Rachats"
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        flux_net = souscriptions - rachats
        
        resultats.append({
            'fcp': fcp.nom,
            'souscriptions': souscriptions,
            'rachats': rachats,
            'flux_net': flux_net
        })
    
    return sorted(resultats, key=lambda x: x['flux_net'], reverse=True)


# ============================================================
# 9. OPTIMISATION DES REQUÊTES
# ============================================================

# Utiliser select_related pour les clés étrangères (1-1, N-1)
operations_optimisees = SouscriptionRachat.objects.select_related(
    'fcp', 'type_client', 'type_operation'
).filter(date__year=2024)

# Utiliser prefetch_related pour les relations inverses (1-N, N-N)
fcps_avec_vl = FCP.objects.prefetch_related(
    'valeurs_liquidatives'
).filter(actif=True)

# Combiner les deux
fcps_complets = FCP.objects.prefetch_related(
    'valeurs_liquidatives',
    'operations',
    'actifs_nets'
).select_related().filter(actif=True)


# ============================================================
# 10. EXPORT ET AGRÉGATIONS
# ============================================================

# Créer un résumé mensuel des opérations
def resume_mensuel(fcp, annee):
    """Créer un résumé mensuel des opérations pour un FCP"""
    from django.db.models.functions import TruncMonth
    
    resume = SouscriptionRachat.objects.filter(
        fcp=fcp,
        date__year=annee
    ).annotate(
        mois=TruncMonth('date')
    ).values('mois').annotate(
        souscriptions=Sum('montant', filter=Q(type_operation__nom='Souscriptions')),
        rachats=Sum('montant', filter=Q(type_operation__nom='Rachats')),
        nb_operations=Count('id')
    ).order_by('mois')
    
    return list(resume)


# Export vers CSV
def export_vl_csv(fcp, fichier='export_vl.csv'):
    """Exporter les VL d'un FCP vers CSV"""
    import csv
    
    vl = ValeurLiquidative.objects.filter(fcp=fcp).order_by('date')
    
    with open(fichier, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Valeur Liquidative'])
        for v in vl:
            writer.writerow([v.date, v.valeur])
    
    print(f"Export terminé: {fichier}")


# ============================================================
# EXEMPLES D'UTILISATION
# ============================================================

if __name__ == '__main__':
    # Exemple 1: Afficher les performances de tous les FCPs
    print("\n=== Performances 2024 ===")
    perfs = comparer_performances(date(2024, 1, 1), date(2024, 12, 31))
    for p in perfs[:5]:
        print(f"{p['fcp']}: {p['performance']:.2f}%")
    
    # Exemple 2: Analyser les flux nets
    print("\n=== Flux Nets 2024 ===")
    flux = analyser_flux_nets(2024)
    for f in flux[:5]:
        print(f"{f['fcp']}: {f['flux_net']:,.2f} (S: {f['souscriptions']:,.2f}, R: {f['rachats']:,.2f})")
    
    # Exemple 3: Afficher les dernières VL
    print("\n=== Dernières Valeurs Liquidatives ===")
    for fcp in FCP.objects.filter(actif=True)[:5]:
        derniere = ValeurLiquidative.objects.filter(fcp=fcp).order_by('-date').first()
        if derniere:
            print(f"{fcp.nom}: {derniere.valeur} ({derniere.date})")
