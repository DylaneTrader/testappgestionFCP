#!/usr/bin/env python
"""
Script pour importer les données de la fiche signalétique des FCP
"""
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestionFCP.settings')
django.setup()

from fcp_app.models import FCP, FicheSignaletique

def clean_decimal_value(value):
    """Nettoie et convertit une valeur en decimal"""
    if pd.isna(value) or value == '' or value == 'Néant':
        return None
    try:
        return float(value)
    except:
        return None

def clean_string_value(value):
    """Nettoie une valeur string"""
    if pd.isna(value) or value == '':
        return None
    return str(value).strip()

def import_fiche_signaletique():
    """Importe les données de la fiche signalétique"""
    
    print("Lecture du fichier Excel...")
    df = pd.read_excel('Fiche signalétique des FCP.xlsx')
    
    # Renommer les colonnes pour faciliter l'accès
    df.columns = [
        'nom_fcp', 'echelle_risque', 'type_fcp', 'horizon_investissement',
        'benchmark_obligataire', 'benchmark_brvmc', 'date_creation',
        'depositaire', 'frais_gestion', 'frais_entree', 'frais_sortie'
    ]
    
    print(f"Nombre de FCP à importer: {len(df)}")
    
    created_count = 0
    updated_count = 0
    
    for idx, row in df.iterrows():
        nom_fcp = clean_string_value(row['nom_fcp'])
        
        if not nom_fcp:
            continue
        
        print(f"\nTraitement de: {nom_fcp}")
        
        # Créer ou récupérer le FCP
        fcp, created = FCP.objects.get_or_create(
            nom=nom_fcp,
            defaults={'actif': True}
        )
        
        if created:
            print(f"  ✓ FCP créé: {nom_fcp}")
        
        # Nettoyer la date de création
        date_creation = None
        if pd.notna(row['date_creation']):
            try:
                if isinstance(row['date_creation'], str):
                    date_creation = datetime.strptime(row['date_creation'], '%Y-%m-%d').date()
                else:
                    date_creation = row['date_creation'].date() if hasattr(row['date_creation'], 'date') else row['date_creation']
            except:
                pass
        
        # Créer ou mettre à jour la fiche signalétique
        fiche, fiche_created = FicheSignaletique.objects.update_or_create(
            fcp=fcp,
            defaults={
                'echelle_risque': int(row['echelle_risque']) if pd.notna(row['echelle_risque']) else None,
                'type_fcp': clean_string_value(row['type_fcp']),
                'horizon_investissement': int(row['horizon_investissement']) if pd.notna(row['horizon_investissement']) else None,
                'benchmark_obligataire': clean_decimal_value(row['benchmark_obligataire']),
                'benchmark_brvmc': clean_decimal_value(row['benchmark_brvmc']),
                'date_creation': date_creation,
                'depositaire': clean_string_value(row['depositaire']),
                'frais_gestion': clean_decimal_value(row['frais_gestion']),
                'frais_entree': clean_string_value(row['frais_entree']),
                'frais_sortie': clean_string_value(row['frais_sortie']),
            }
        )
        
        if fiche_created:
            created_count += 1
            print(f"  ✓ Fiche signalétique créée")
        else:
            updated_count += 1
            print(f"  ✓ Fiche signalétique mise à jour")
    
    print(f"\n{'='*60}")
    print(f"Import terminé !")
    print(f"Fiches créées: {created_count}")
    print(f"Fiches mises à jour: {updated_count}")
    print(f"Total: {created_count + updated_count}")

if __name__ == '__main__':
    import_fiche_signaletique()
