"""
Script pour mettre à jour la base de données depuis Excel
Permet d'ajouter de nouvelles données sans tout réimporter
"""
import os
import sys
import django
import pandas as pd
from decimal import Decimal
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionFCP.settings')
django.setup()

from fcp_app.models import (
    FCP, ValeurLiquidative, SouscriptionRachat, ActifNet, 
    Benchmark, PoidsQuotidien, TypeClient, TypeOperation
)


def safe_decimal(value):
    """Convertir en Decimal de manière sûre"""
    if pd.isna(value) or value is None:
        return None
    try:
        return Decimal(str(value))
    except:
        return None


def update_valeurs_liquidatives(date_debut=None):
    """Mettre à jour les valeurs liquidatives depuis une date"""
    print("\n" + "="*60)
    print("MISE À JOUR DES VALEURS LIQUIDATIVES")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Valeurs Liquidatives')
    
    # Filtrer par date si spécifié
    if date_debut:
        df = df[df['Date'] >= date_debut]
        print(f"\nFiltre appliqué: dates >= {date_debut}")
    
    print(f"Nombre de dates à traiter: {len(df)}")
    
    fcp_columns = [col for col in df.columns if col != 'Date']
    valeurs = []
    updates = 0
    
    for idx, row in df.iterrows():
        date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
        
        for fcp_nom in fcp_columns:
            fcp = FCP.objects.get(nom=fcp_nom)
            valeur = safe_decimal(row[fcp_nom])
            
            if valeur is not None:
                # Vérifier si existe déjà
                exists = ValeurLiquidative.objects.filter(fcp=fcp, date=date).exists()
                
                if not exists:
                    valeurs.append(ValeurLiquidative(
                        fcp=fcp,
                        date=date,
                        valeur=valeur
                    ))
                    updates += 1
        
        if (idx + 1) % 50 == 0:
            print(f"  Traité: {idx + 1}/{len(df)} lignes")
    
    if valeurs:
        ValeurLiquidative.objects.bulk_create(valeurs, batch_size=1000)
        print(f"\n✅ {updates} nouvelles valeurs liquidatives ajoutées")
    else:
        print(f"\n✅ Aucune nouvelle donnée à ajouter")


def update_souscriptions_rachats(date_debut=None):
    """Mettre à jour les souscriptions/rachats"""
    print("\n" + "="*60)
    print("MISE À JOUR DES SOUSCRIPTIONS/RACHATS")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Souscriptions Rachats')
    
    if date_debut:
        df = df[df['Date'] >= date_debut]
        print(f"\nFiltre appliqué: dates >= {date_debut}")
    
    print(f"Nombre d'opérations à traiter: {len(df)}")
    
    operations = []
    updates = 0
    
    for idx, row in df.iterrows():
        try:
            date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
            fcp = FCP.objects.get(nom=row['FCP'])
            type_client = TypeClient.objects.get(nom=row['Type de clients'])
            type_operation = TypeOperation.objects.get(nom=row['Opérations'])
            montant = safe_decimal(row['Montant'])
            
            # Vérifier si existe (approximativement - même date, FCP, type_op, montant)
            exists = SouscriptionRachat.objects.filter(
                date=date,
                fcp=fcp,
                type_operation=type_operation,
                montant=montant
            ).exists()
            
            if not exists and montant is not None:
                operations.append(SouscriptionRachat(
                    date=date,
                    type_client=type_client,
                    type_operation=type_operation,
                    fcp=fcp,
                    montant=montant
                ))
                updates += 1
            
            if (idx + 1) % 100 == 0:
                print(f"  Traité: {idx + 1}/{len(df)} lignes")
        except Exception as e:
            print(f"  ⚠️ Erreur ligne {idx}: {e}")
    
    if operations:
        SouscriptionRachat.objects.bulk_create(operations, batch_size=1000)
        print(f"\n✅ {updates} nouvelles opérations ajoutées")
    else:
        print(f"\n✅ Aucune nouvelle donnée à ajouter")


def update_actifs_nets(date_debut=None):
    """Mettre à jour les actifs nets"""
    print("\n" + "="*60)
    print("MISE À JOUR DES ACTIFS NETS")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Actifs Nets')
    
    if date_debut:
        df = df[df['Date'] >= date_debut]
        print(f"\nFiltre appliqué: dates >= {date_debut}")
    
    print(f"Nombre de dates à traiter: {len(df)}")
    
    fcp_columns = [col for col in df.columns if col != 'Date']
    actifs = []
    updates = 0
    
    for idx, row in df.iterrows():
        date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
        
        for fcp_nom in fcp_columns:
            try:
                fcp = FCP.objects.get(nom=fcp_nom)
                montant = safe_decimal(row[fcp_nom])
                
                if montant is not None:
                    exists = ActifNet.objects.filter(fcp=fcp, date=date).exists()
                    
                    if not exists:
                        actifs.append(ActifNet(
                            fcp=fcp,
                            date=date,
                            montant=montant
                        ))
                        updates += 1
            except FCP.DoesNotExist:
                continue
        
        if (idx + 1) % 50 == 0:
            print(f"  Traité: {idx + 1}/{len(df)} lignes")
    
    if actifs:
        ActifNet.objects.bulk_create(actifs, batch_size=1000)
        print(f"\n✅ {updates} nouveaux actifs nets ajoutés")
    else:
        print(f"\n✅ Aucune nouvelle donnée à ajouter")


def update_benchmarks(date_debut=None):
    """Mettre à jour les benchmarks"""
    print("\n" + "="*60)
    print("MISE À JOUR DES BENCHMARKS")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Benchmarks')
    
    if date_debut:
        df = df[df['Date'] >= date_debut]
        print(f"\nFiltre appliqué: dates >= {date_debut}")
    
    print(f"Nombre de benchmarks à traiter: {len(df)}")
    
    benchmarks = []
    updates = 0
    
    for idx, row in df.iterrows():
        date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
        
        exists = Benchmark.objects.filter(date=date).exists()
        
        if not exists:
            benchmarks.append(Benchmark(
                date=date,
                benchmark_obligataire=safe_decimal(row['Benchmark Obligataire']),
                benchmark_actions=safe_decimal(row['Benchmark Actions'])
            ))
            updates += 1
        
        if (idx + 1) % 50 == 0:
            print(f"  Traité: {idx + 1}/{len(df)} lignes")
    
    if benchmarks:
        Benchmark.objects.bulk_create(benchmarks, batch_size=1000)
        print(f"\n✅ {updates} nouveaux benchmarks ajoutés")
    else:
        print(f"\n✅ Aucune nouvelle donnée à ajouter")


def update_poids_quotidiens(date_debut=None):
    """Mettre à jour les poids quotidiens"""
    print("\n" + "="*60)
    print("MISE À JOUR DES POIDS QUOTIDIENS")
    print("="*60)
    
    df = pd.read_excel('data_fcp.xlsx', sheet_name='Poids Quotidiens')
    
    if date_debut:
        df = df[df['Date'] >= date_debut]
        print(f"\nFiltre appliqué: dates >= {date_debut}")
    
    print(f"Nombre de poids à traiter: {len(df)}")
    
    poids = []
    updates = 0
    
    for idx, row in df.iterrows():
        try:
            date = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
            fcp = FCP.objects.get(nom=row['FCP'])
            
            exists = PoidsQuotidien.objects.filter(fcp=fcp, date=date).exists()
            
            if not exists:
                poids.append(PoidsQuotidien(
                    fcp=fcp,
                    date=date,
                    actions=safe_decimal(row['Actions']),
                    obligations=safe_decimal(row['Obligations']),
                    opcvm=safe_decimal(row['OPCVM']),
                    liquidites=safe_decimal(row['Liquidités'])
                ))
                updates += 1
            
            if (idx + 1) % 500 == 0:
                print(f"  Traité: {idx + 1}/{len(df)} lignes")
        except Exception as e:
            print(f"  ⚠️ Erreur ligne {idx}: {e}")
    
    if poids:
        PoidsQuotidien.objects.bulk_create(poids, batch_size=1000)
        print(f"\n✅ {updates} nouveaux poids quotidiens ajoutés")
    else:
        print(f"\n✅ Aucune nouvelle donnée à ajouter")


def get_derniere_date():
    """Obtenir la dernière date dans la base de données"""
    dates = []
    
    derniere_vl = ValeurLiquidative.objects.order_by('-date').first()
    if derniere_vl:
        dates.append(derniere_vl.date)
    
    dernier_actif = ActifNet.objects.order_by('-date').first()
    if dernier_actif:
        dates.append(dernier_actif.date)
    
    dernier_benchmark = Benchmark.objects.order_by('-date').first()
    if dernier_benchmark:
        dates.append(dernier_benchmark.date)
    
    return max(dates) if dates else None


def main():
    """Fonction principale de mise à jour"""
    print("\n" + "="*60)
    print("MISE À JOUR DE LA BASE DE DONNÉES")
    print("="*60)
    print(f"\nDébut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Obtenir la dernière date dans la BD
        derniere_date = get_derniere_date()
        
        if derniere_date:
            print(f"\nDernière date dans la base: {derniere_date}")
            reponse = input("\nVoulez-vous mettre à jour depuis cette date ? (o/n): ")
            
            if reponse.lower() == 'o':
                date_debut = derniere_date
            else:
                date_str = input("Entrez la date de début (YYYY-MM-DD) ou laissez vide pour tout: ")
                date_debut = pd.to_datetime(date_str).date() if date_str else None
        else:
            print("\nAucune donnée dans la base. Migration complète...")
            date_debut = None
        
        # Mettre à jour toutes les tables
        update_valeurs_liquidatives(date_debut)
        update_souscriptions_rachats(date_debut)
        update_actifs_nets(date_debut)
        update_benchmarks(date_debut)
        update_poids_quotidiens(date_debut)
        
        print("\n" + "="*60)
        print("✅ MISE À JOUR TERMINÉE AVEC SUCCÈS")
        print("="*60)
        
        # Statistiques finales
        print("\nStatistiques actuelles:")
        print(f"  - Valeurs Liquidatives: {ValeurLiquidative.objects.count()}")
        print(f"  - Souscriptions/Rachats: {SouscriptionRachat.objects.count()}")
        print(f"  - Actifs Nets: {ActifNet.objects.count()}")
        print(f"  - Benchmarks: {Benchmark.objects.count()}")
        print(f"  - Poids Quotidiens: {PoidsQuotidien.objects.count()}")
        
        print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Opération annulée par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
