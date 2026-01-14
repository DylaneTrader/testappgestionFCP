"""
Commande Django pour importer les valeurs liquidatives depuis le fichier Excel
dans les 25 tables VL séparées
"""
import pandas as pd
from django.core.management.base import BaseCommand
from fcp_app.models import FicheSignaletique, FCP_VL_MODELS, get_vl_model
from decimal import Decimal
from datetime import datetime


class Command(BaseCommand):
    help = 'Importe les valeurs liquidatives depuis le fichier Excel dans les 25 tables VL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data_fcp (3).xlsx',
            help='Chemin vers le fichier Excel'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprimer toutes les VL existantes avant import'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        self.stdout.write(f'Lecture du fichier: {file_path}')
        
        # Lire le fichier Excel
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lecture fichier: {e}'))
            return
        
        self.stdout.write(f'  → {len(df)} lignes, {len(df.columns)} colonnes')
        
        # Récupérer les FCP existants
        fcp_dict = {fcp.nom: fcp for fcp in FicheSignaletique.objects.all()}
        self.stdout.write(f'  → {len(fcp_dict)} FCP en base')
        
        # Colonnes FCP (toutes sauf Date)
        fcp_columns = [col for col in df.columns if col != 'Date']
        
        # Supprimer les VL existantes si demandé
        if options['clear']:
            self.stdout.write('')
            self.stdout.write('Suppression des VL existantes...')
            for fcp_name, model_class in FCP_VL_MODELS.items():
                deleted, _ = model_class.objects.all().delete()
                if deleted > 0:
                    self.stdout.write(f'  {fcp_name}: {deleted} supprimées')
        
        # Importer les données par FCP
        self.stdout.write('')
        self.stdout.write('Import en cours...')
        
        total_created = 0
        
        for fcp_name in fcp_columns:
            # Récupérer le modèle VL correspondant
            vl_model = get_vl_model(fcp_name)
            
            if vl_model is None:
                self.stdout.write(self.style.WARNING(f'  ⚠ Modèle non trouvé pour: {fcp_name}'))
                continue
            
            # Récupérer l'objet FCP
            fcp_obj = fcp_dict.get(fcp_name)
            if fcp_obj is None:
                self.stdout.write(self.style.WARNING(f'  ⚠ FCP non trouvé en base: {fcp_name}'))
                continue
            
            # Supprimer les données existantes pour ce FCP
            vl_model.objects.all().delete()
            
            # Préparer les objets VL
            vl_objects = []
            skipped = 0
            
            for idx, row in df.iterrows():
                date_val = row['Date']
                valeur = row[fcp_name]
                
                # Ignorer les valeurs nulles
                if pd.isna(date_val) or pd.isna(valeur):
                    skipped += 1
                    continue
                
                # Convertir la date
                if isinstance(date_val, datetime):
                    date = date_val.date()
                elif isinstance(date_val, str):
                    date = datetime.strptime(date_val, '%Y-%m-%d').date()
                else:
                    date = date_val
                
                vl_objects.append(vl_model(
                    fcp=fcp_obj,
                    date=date,
                    valeur=Decimal(str(valeur))
                ))
            
            # Bulk create
            if vl_objects:
                vl_model.objects.bulk_create(vl_objects, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(f'  ✓ {fcp_name}: {len(vl_objects)} VL'))
                total_created += len(vl_objects)
            else:
                self.stdout.write(f'  - {fcp_name}: 0 VL (toutes nulles)')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Import terminé! {total_created} VL créées au total.'))
