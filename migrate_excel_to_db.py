"""
Script de migration des données Excel vers la base de données SQL
"""
import os
import sys
import django
import pandas as pd
from decimal import Decimal
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionFCP.settings')
django.setup()

from fcp_app.models import (
    FCP, ValeurLiquidative, TypeClient, TypeOperation, SouscriptionRachat,
    ActifNet, TypeFCP, ClasseActif, Secteur, Pays, SecteurObligation,
    Cotation, CompositionFCP, Benchmark, PoidsQuotidien
)


def safe_decimal(value):
    """Convertir une valeur en Decimal de manière sûre"""
    if pd.isna(value) or value is None:
        return None
    try:
        return Decimal(str(value))
    except:
        return None


def get_or_create_fcp(nom):
    """Obtenir ou créer un FCP"""
    fcp, created = FCP.objects.get_or_create(nom=nom)
    if created:
        print(f"  ✓ FCP créé: {nom}")
    return fcp


def migrate_valeurs_liquidatives():
    """Migrer les valeurs liquidatives"""
    print("\n" + "="*60)
    print("Migration des Valeurs Liquidatives")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Valeurs Liquidatives')
    
    # Créer tous les FCPs
    fcp_columns = [col for col in df.columns if col != 'Date']
    fcps = {col: get_or_create_fcp(col) for col in fcp_columns}
    
    print(f"\nTraitement de {len(df)} dates...")
    
    valeurs = []
    for idx, row in df.iterrows():
        date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
        
        for fcp_nom, fcp_obj in fcps.items():
            valeur = safe_decimal(row[fcp_nom])
            if valeur is not None:
                valeurs.append(ValeurLiquidative(
                    fcp=fcp_obj,
                    date=date,
                    valeur=valeur
                ))
        
        if (idx + 1) % 100 == 0:
            print(f"  Traité: {idx + 1}/{len(df)} lignes")
    
    # Insertion en bulk
    ValeurLiquidative.objects.bulk_create(valeurs, ignore_conflicts=True, batch_size=1000)
    print(f"✓ {len(valeurs)} valeurs liquidatives insérées")


def migrate_souscriptions_rachats():
    """Migrer les souscriptions et rachats"""
    print("\n" + "="*60)
    print("Migration des Souscriptions et Rachats")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Souscriptions Rachats')
    
    # Créer les types de clients
    types_clients = {}
    for tc in df['Type de clients'].unique():
        if pd.notna(tc):
            obj, created = TypeClient.objects.get_or_create(nom=tc)
            types_clients[tc] = obj
            if created:
                print(f"  ✓ Type client créé: {tc}")
    
    # Créer les types d'opérations
    types_operations = {}
    for to in df['Opérations'].unique():
        if pd.notna(to):
            obj, created = TypeOperation.objects.get_or_create(nom=to)
            types_operations[to] = obj
            if created:
                print(f"  ✓ Type opération créé: {to}")
    
    print(f"\nTraitement de {len(df)} opérations...")
    
    operations = []
    for idx, row in df.iterrows():
        try:
            date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
            fcp = get_or_create_fcp(row['FCP'])
            type_client = types_clients.get(row['Type de clients'])
            type_operation = types_operations.get(row['Opérations'])
            montant = safe_decimal(row['Montant'])
            
            if type_client and type_operation and montant is not None:
                operations.append(SouscriptionRachat(
                    date=date,
                    type_client=type_client,
                    type_operation=type_operation,
                    fcp=fcp,
                    montant=montant
                ))
            
            if (idx + 1) % 500 == 0:
                print(f"  Traité: {idx + 1}/{len(df)} lignes")
        except Exception as e:
            print(f"  ⚠ Erreur ligne {idx}: {e}")
    
    SouscriptionRachat.objects.bulk_create(operations, batch_size=1000)
    print(f"✓ {len(operations)} opérations insérées")


def migrate_actifs_nets():
    """Migrer les actifs nets"""
    print("\n" + "="*60)
    print("Migration des Actifs Nets")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Actifs Nets')
    
    fcp_columns = [col for col in df.columns if col != 'Date']
    fcps = {col: get_or_create_fcp(col) for col in fcp_columns}
    
    print(f"\nTraitement de {len(df)} dates...")
    
    actifs = []
    for idx, row in df.iterrows():
        date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
        
        for fcp_nom, fcp_obj in fcps.items():
            montant = safe_decimal(row[fcp_nom])
            if montant is not None:
                actifs.append(ActifNet(
                    fcp=fcp_obj,
                    date=date,
                    montant=montant
                ))
        
        if (idx + 1) % 100 == 0:
            print(f"  Traité: {idx + 1}/{len(df)} lignes")
    
    ActifNet.objects.bulk_create(actifs, ignore_conflicts=True, batch_size=1000)
    print(f"✓ {len(actifs)} actifs nets insérés")


def migrate_composition_fcp():
    """Migrer la composition des FCP"""
    print("\n" + "="*60)
    print("Migration de la Composition des FCP")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Composition FCP')
    
    # Créer les types de FCP
    types_fcp = {}
    for tf in df['Type FCP'].unique():
        if pd.notna(tf):
            obj, created = TypeFCP.objects.get_or_create(nom=tf)
            types_fcp[tf] = obj
            if created:
                print(f"  ✓ Type FCP créé: {tf}")
    
    # Créer les classes d'actifs
    classes = {}
    for cl in df['Classe'].unique():
        if pd.notna(cl):
            obj, created = ClasseActif.objects.get_or_create(nom=cl)
            classes[cl] = obj
            if created:
                print(f"  ✓ Classe créée: {cl}")
    
    # Créer les secteurs
    secteurs = {}
    for sec in df['Secteur'].unique():
        if pd.notna(sec):
            obj, created = Secteur.objects.get_or_create(nom=sec)
            secteurs[sec] = obj
            if created:
                print(f"  ✓ Secteur créé: {sec}")
    
    # Créer les pays
    pays_dict = {}
    for p in df['Pays'].unique():
        if pd.notna(p):
            obj, created = Pays.objects.get_or_create(nom=p)
            pays_dict[p] = obj
            if created:
                print(f"  ✓ Pays créé: {p}")
    
    # Créer les secteurs obligations
    secteurs_oblig = {}
    for so in df['Secteur Obligation'].unique():
        if pd.notna(so):
            obj, created = SecteurObligation.objects.get_or_create(nom=so)
            secteurs_oblig[so] = obj
            if created:
                print(f"  ✓ Secteur obligation créé: {so}")
    
    # Créer les cotations
    cotations = {}
    for cot in df['Cotation'].unique():
        if pd.notna(cot):
            obj, created = Cotation.objects.get_or_create(nom=cot)
            cotations[cot] = obj
            if created:
                print(f"  ✓ Cotation créée: {cot}")
    
    print(f"\nTraitement de {len(df)} compositions...")
    
    compositions = []
    for idx, row in df.iterrows():
        try:
            fcp = get_or_create_fcp(row['FCP'])
            pourcentage = safe_decimal(row['Pourcentage'])
            
            if pourcentage is not None:
                compositions.append(CompositionFCP(
                    fcp=fcp,
                    type_fcp=types_fcp.get(row['Type FCP']),
                    classe=classes.get(row['Classe']),
                    secteur=secteurs.get(row['Secteur']),
                    pays=pays_dict.get(row['Pays']),
                    secteur_obligation=secteurs_oblig.get(row['Secteur Obligation']),
                    cotation=cotations.get(row['Cotation']),
                    pourcentage=pourcentage
                ))
            
            if (idx + 1) % 500 == 0:
                print(f"  Traité: {idx + 1}/{len(df)} lignes")
        except Exception as e:
            print(f"  ⚠ Erreur ligne {idx}: {e}")
    
    CompositionFCP.objects.bulk_create(compositions, batch_size=1000)
    print(f"✓ {len(compositions)} compositions insérées")


def migrate_benchmarks():
    """Migrer les benchmarks"""
    print("\n" + "="*60)
    print("Migration des Benchmarks")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Benchmarks')
    
    print(f"\nTraitement de {len(df)} benchmarks...")
    
    benchmarks = []
    for idx, row in df.iterrows():
        date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
        
        benchmarks.append(Benchmark(
            date=date,
            benchmark_obligataire=safe_decimal(row['Benchmark Obligataire']),
            benchmark_actions=safe_decimal(row['Benchmark Actions'])
        ))
        
        if (idx + 1) % 100 == 0:
            print(f"  Traité: {idx + 1}/{len(df)} lignes")
    
    Benchmark.objects.bulk_create(benchmarks, ignore_conflicts=True, batch_size=1000)
    print(f"✓ {len(benchmarks)} benchmarks insérés")


def migrate_poids_quotidiens():
    """Migrer les poids quotidiens"""
    print("\n" + "="*60)
    print("Migration des Poids Quotidiens")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Poids Quotidiens')
    
    print(f"\nTraitement de {len(df)} poids quotidiens...")
    
    poids = []
    for idx, row in df.iterrows():
        try:
            date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
            fcp = get_or_create_fcp(row['FCP'])
            
            poids.append(PoidsQuotidien(
                fcp=fcp,
                date=date,
                actions=safe_decimal(row['Actions']),
                obligations=safe_decimal(row['Obligations']),
                opcvm=safe_decimal(row['OPCVM']),
                liquidites=safe_decimal(row['Liquidités'])
            ))
            
            if (idx + 1) % 1000 == 0:
                print(f"  Traité: {idx + 1}/{len(df)} lignes")
        except Exception as e:
            print(f"  ⚠ Erreur ligne {idx}: {e}")
    
    PoidsQuotidien.objects.bulk_create(poids, ignore_conflicts=True, batch_size=1000)
    print(f"✓ {len(poids)} poids quotidiens insérés")


def main():
    """Fonction principale de migration"""
    print("\n" + "="*60)
    print("MIGRATION DES DONNÉES EXCEL VERS SQL")
    print("="*60)
    print(f"\nDébut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Ordre important pour respecter les dépendances
        migrate_valeurs_liquidatives()
        migrate_souscriptions_rachats()
        migrate_actifs_nets()
        migrate_composition_fcp()
        migrate_benchmarks()
        migrate_poids_quotidiens()
        
        print("\n" + "="*60)
        print("✓ MIGRATION TERMINÉE AVEC SUCCÈS")
        print("="*60)
        
        # Statistiques finales
        print("\nStatistiques:")
        print(f"  - FCPs: {FCP.objects.count()}")
        print(f"  - Valeurs Liquidatives: {ValeurLiquidative.objects.count()}")
        print(f"  - Souscriptions/Rachats: {SouscriptionRachat.objects.count()}")
        print(f"  - Actifs Nets: {ActifNet.objects.count()}")
        print(f"  - Compositions: {CompositionFCP.objects.count()}")
        print(f"  - Benchmarks: {Benchmark.objects.count()}")
        print(f"  - Poids Quotidiens: {PoidsQuotidien.objects.count()}")
        
        print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
