"""
Script de comparaison de performance: Excel vs Base SQL
Démontre les avantages de performance de la base SQL
"""
import time
import pandas as pd
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionFCP.settings')
django.setup()

from fcp_app.models import FCP, ValeurLiquidative, SouscriptionRachat, ActifNet
from django.db.models import Sum, Avg, Max, Min, Count


def benchmark_excel():
    """Mesurer le temps de lecture et traitement avec Excel"""
    print("\n" + "="*60)
    print("BENCHMARK EXCEL")
    print("="*60)
    
    # Test 1: Charger toutes les valeurs liquidatives
    start = time.time()
    df_vl = pd.read_excel('data_fcp.xlsx', sheet_name='Valeurs Liquidatives')
    temps_chargement = time.time() - start
    print(f"\n1. Chargement Valeurs Liquidatives: {temps_chargement:.3f}s")
    print(f"   Lignes chargées: {len(df_vl)}")
    
    # Test 2: Filtrer les VL d'un FCP spécifique
    start = time.time()
    vl_fcp = df_vl[['Date', 'FCP ACTIONS PHARMACIE']].dropna()
    temps_filtre = time.time() - start
    print(f"\n2. Filtrage pour un FCP: {temps_filtre:.3f}s")
    print(f"   Lignes filtrées: {len(vl_fcp)}")
    
    # Test 3: Calculer des statistiques
    start = time.time()
    stats = {
        'max': df_vl['FCP ACTIONS PHARMACIE'].max(),
        'min': df_vl['FCP ACTIONS PHARMACIE'].min(),
        'avg': df_vl['FCP ACTIONS PHARMACIE'].mean()
    }
    temps_stats = time.time() - start
    print(f"\n3. Calcul statistiques: {temps_stats:.3f}s")
    print(f"   Stats: Max={stats['max']:.2f}, Min={stats['min']:.2f}, Avg={stats['avg']:.2f}")
    
    # Test 4: Charger et joindre plusieurs feuilles
    start = time.time()
    df_ops = pd.read_excel('data_fcp.xlsx', sheet_name='Souscriptions Rachats')
    df_actifs = pd.read_excel('data_fcp.xlsx', sheet_name='Actifs Nets')
    temps_multi = time.time() - start
    print(f"\n4. Chargement de 2 autres feuilles: {temps_multi:.3f}s")
    
    # Test 5: Agrégation complexe
    start = time.time()
    ops_fcp = df_ops[df_ops['FCP'] == 'FCP ACTIONS PHARMACIE']
    total_par_type = ops_fcp.groupby('Opérations')['Montant'].sum()
    temps_aggreg = time.time() - start
    print(f"\n5. Agrégation par type d'opération: {temps_aggreg:.3f}s")
    
    temps_total_excel = temps_chargement + temps_filtre + temps_stats + temps_multi + temps_aggreg
    print(f"\n⏱️  TOTAL EXCEL: {temps_total_excel:.3f}s")
    
    return temps_total_excel


def benchmark_sql():
    """Mesurer le temps de requêtes avec SQL"""
    print("\n" + "="*60)
    print("BENCHMARK SQL")
    print("="*60)
    
    fcp = FCP.objects.get(nom="FCP ACTIONS PHARMACIE")
    
    # Test 1: Charger toutes les valeurs liquidatives
    start = time.time()
    vl_all = list(ValeurLiquidative.objects.all())
    temps_chargement = time.time() - start
    print(f"\n1. Chargement Valeurs Liquidatives: {temps_chargement:.3f}s")
    print(f"   Lignes chargées: {len(vl_all)}")
    
    # Test 2: Filtrer les VL d'un FCP spécifique
    start = time.time()
    vl_fcp = list(ValeurLiquidative.objects.filter(fcp=fcp))
    temps_filtre = time.time() - start
    print(f"\n2. Filtrage pour un FCP: {temps_filtre:.3f}s")
    print(f"   Lignes filtrées: {len(vl_fcp)}")
    
    # Test 3: Calculer des statistiques
    start = time.time()
    stats = ValeurLiquidative.objects.filter(fcp=fcp).aggregate(
        max_vl=Max('valeur'),
        min_vl=Min('valeur'),
        avg_vl=Avg('valeur')
    )
    temps_stats = time.time() - start
    print(f"\n3. Calcul statistiques: {temps_stats:.3f}s")
    print(f"   Stats: Max={stats['max_vl']:.2f}, Min={stats['min_vl']:.2f}, Avg={stats['avg_vl']:.2f}")
    
    # Test 4: Charger données de plusieurs tables
    start = time.time()
    ops = list(SouscriptionRachat.objects.all())
    actifs = list(ActifNet.objects.all())
    temps_multi = time.time() - start
    print(f"\n4. Chargement de 2 autres tables: {temps_multi:.3f}s")
    
    # Test 5: Agrégation complexe
    start = time.time()
    total_par_type = SouscriptionRachat.objects.filter(fcp=fcp).values(
        'type_operation__nom'
    ).annotate(
        total=Sum('montant')
    )
    list(total_par_type)  # Force l'évaluation
    temps_aggreg = time.time() - start
    print(f"\n5. Agrégation par type d'opération: {temps_aggreg:.3f}s")
    
    temps_total_sql = temps_chargement + temps_filtre + temps_stats + temps_multi + temps_aggreg
    print(f"\n⏱️  TOTAL SQL: {temps_total_sql:.3f}s")
    
    return temps_total_sql


def benchmark_requetes_complexes():
    """Comparer des requêtes complexes"""
    print("\n" + "="*60)
    print("BENCHMARK REQUÊTES COMPLEXES")
    print("="*60)
    
    # Test Excel: Calculer les flux nets par FCP
    print("\n📊 Test: Flux nets de tous les FCPs")
    start = time.time()
    df_ops = pd.read_excel('data_fcp.xlsx', sheet_name='Souscriptions Rachats')
    flux_excel = {}
    for fcp_nom in df_ops['FCP'].unique():
        df_fcp = df_ops[df_ops['FCP'] == fcp_nom]
        souscriptions = df_fcp[df_fcp['Opérations'] == 'Souscriptions']['Montant'].sum()
        rachats = df_fcp[df_fcp['Opérations'] == 'Rachats']['Montant'].sum()
        flux_excel[fcp_nom] = souscriptions - rachats
    temps_excel = time.time() - start
    print(f"   Excel: {temps_excel:.3f}s")
    
    # Test SQL: Même calcul
    start = time.time()
    fcps = FCP.objects.all()
    flux_sql = {}
    for fcp in fcps:
        souscriptions = SouscriptionRachat.objects.filter(
            fcp=fcp,
            type_operation__nom="Souscriptions"
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        rachats = SouscriptionRachat.objects.filter(
            fcp=fcp,
            type_operation__nom="Rachats"
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        flux_sql[fcp.nom] = souscriptions - rachats
    temps_sql = time.time() - start
    print(f"   SQL: {temps_sql:.3f}s")
    
    gain = ((temps_excel - temps_sql) / temps_excel) * 100
    print(f"   💡 Gain SQL: {gain:.1f}% plus rapide")
    
    # Test 2: Dernières valeurs de tous les FCPs
    print("\n📊 Test: Dernières valeurs liquidatives de tous les FCPs")
    start = time.time()
    df_vl = pd.read_excel('data_fcp.xlsx', sheet_name='Valeurs Liquidatives')
    dernieres_excel = {}
    derniere_date = df_vl['Date'].max()
    derniere_ligne = df_vl[df_vl['Date'] == derniere_date].iloc[0]
    for col in df_vl.columns:
        if col != 'Date':
            dernieres_excel[col] = derniere_ligne[col]
    temps_excel2 = time.time() - start
    print(f"   Excel: {temps_excel2:.3f}s")
    
    start = time.time()
    dernieres_sql = {}
    for fcp in FCP.objects.all():
        derniere = ValeurLiquidative.objects.filter(fcp=fcp).order_by('-date').first()
        if derniere:
            dernieres_sql[fcp.nom] = derniere.valeur
    temps_sql2 = time.time() - start
    print(f"   SQL: {temps_sql2:.3f}s")
    
    gain2 = ((temps_excel2 - temps_sql2) / temps_excel2) * 100
    print(f"   💡 Gain SQL: {gain2:.1f}% plus rapide")


def benchmark_memoire():
    """Comparer l'utilisation mémoire"""
    print("\n" + "="*60)
    print("BENCHMARK MÉMOIRE")
    print("="*60)
    
    import sys
    
    # Test Excel
    df_vl = pd.read_excel('data_fcp.xlsx', sheet_name='Valeurs Liquidatives')
    df_ops = pd.read_excel('data_fcp.xlsx', sheet_name='Souscriptions Rachats')
    df_actifs = pd.read_excel('data_fcp.xlsx', sheet_name='Actifs Nets')
    
    memoire_excel = (
        sys.getsizeof(df_vl) + 
        sys.getsizeof(df_ops) + 
        sys.getsizeof(df_actifs)
    ) / (1024 * 1024)  # En MB
    
    print(f"\n📊 Mémoire utilisée par les DataFrames Excel: {memoire_excel:.2f} MB")
    
    # Avec SQL, on ne charge que ce dont on a besoin
    fcp = FCP.objects.first()
    vl_sql = ValeurLiquidative.objects.filter(fcp=fcp)[:100]
    
    print(f"\n📊 Avec SQL: Chargement à la demande, pas de chargement complet en mémoire")
    print(f"   Exemple: {len(vl_sql)} enregistrements chargés au lieu de {len(df_vl)}")


def main():
    """Exécuter tous les benchmarks"""
    print("\n" + "="*60)
    print("COMPARAISON DE PERFORMANCE: EXCEL vs SQL")
    print("="*60)
    
    try:
        temps_excel = benchmark_excel()
        temps_sql = benchmark_sql()
        
        print("\n" + "="*60)
        print("RÉSULTAT GLOBAL")
        print("="*60)
        print(f"\n⏱️  Temps total Excel: {temps_excel:.3f}s")
        print(f"⏱️  Temps total SQL: {temps_sql:.3f}s")
        
        if temps_sql < temps_excel:
            gain = ((temps_excel - temps_sql) / temps_excel) * 100
            facteur = temps_excel / temps_sql
            print(f"\n✅ SQL est {gain:.1f}% plus rapide ({facteur:.1f}x)")
        
        benchmark_requetes_complexes()
        benchmark_memoire()
        
        print("\n" + "="*60)
        print("AVANTAGES DE LA BASE SQL")
        print("="*60)
        print("""
✅ Performance: Requêtes indexées ultra-rapides
✅ Scalabilité: Gère facilement des millions d'enregistrements
✅ Intégrité: Contraintes et validations automatiques
✅ Concurrence: Plusieurs utilisateurs simultanés
✅ Transactions: Opérations atomiques sécurisées
✅ Optimisation: Requêtes optimisées automatiquement
✅ Mémoire: Chargement à la demande, pas de chargement complet
✅ Maintenance: Ajout/modification facile des données
✅ Backup: Sauvegardes incrémentielles possibles
✅ Relations: Gestion automatique des clés étrangères
        """)
        
        print("\n" + "="*60)
        print("QUAND UTILISER EXCEL VS SQL")
        print("="*60)
        print("""
📊 Excel convient pour:
   - Prototypes rapides
   - Petits volumes de données (< 10 000 lignes)
   - Analyse ponctuelle
   - Visualisations simples
   - Partage de fichiers standalone

🗄️  SQL convient pour:
   - Applications web
   - Gros volumes de données (> 10 000 lignes)
   - Données relationnelles complexes
   - Accès concurrent multiple
   - Performance critique
   - Intégrité des données importante
   - Évolutivité à long terme
        """)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
