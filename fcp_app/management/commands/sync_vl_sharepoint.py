"""
Commande Django pour synchroniser les valeurs liquidatives depuis SharePoint
- Connexion et téléchargement du fichier Excel depuis SharePoint
- Lecture du fichier (feuille spécifique)
- Insertion incrémentale dans chaque table VL
- Logging d'exécution détaillé
"""
import os
import io
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings

from fcp_app.models import FicheSignaletique, FCP_VL_MODELS, get_vl_model

# Configuration du logging
LOG_DIR = Path(settings.BASE_DIR) / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger('sync_vl_sharepoint')
logger.setLevel(logging.DEBUG)

# Handler fichier
file_handler = logging.FileHandler(
    LOG_DIR / 'sync_vl_sharepoint.log',
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(file_handler)


class Command(BaseCommand):
    help = 'Synchronise les valeurs liquidatives depuis SharePoint (insertion incrémentale)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site-url',
            type=str,
            required=True,
            help='URL du site SharePoint (ex: https://votretenant.sharepoint.com/sites/VotreSite)'
        )
        parser.add_argument(
            '--file-path',
            type=str,
            required=True,
            help='Chemin relatif du fichier Excel dans SharePoint (ex: Documents partages/VL/data_vl.xlsx)'
        )
        parser.add_argument(
            '--sheet-name',
            type=str,
            default='VL',
            help='Nom de la feuille Excel à lire (défaut: VL)'
        )
        parser.add_argument(
            '--client-id',
            type=str,
            help='Client ID Azure AD (ou définir SHAREPOINT_CLIENT_ID en variable d\'environnement)'
        )
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Client Secret Azure AD (ou définir SHAREPOINT_CLIENT_SECRET en variable d\'environnement)'
        )
        parser.add_argument(
            '--tenant-id',
            type=str,
            help='Tenant ID Azure AD (ou définir SHAREPOINT_TENANT_ID en variable d\'environnement)'
        )
        parser.add_argument(
            '--local-file',
            type=str,
            help='Utiliser un fichier local au lieu de SharePoint (pour tests)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode simulation : affiche les opérations sans les exécuter'
        )

    def log_and_print(self, message, level='info', style=None):
        """Log et affiche un message"""
        getattr(logger, level)(message)
        if style:
            self.stdout.write(style(message))
        else:
            self.stdout.write(message)

    def download_from_sharepoint(self, site_url, file_path, client_id, client_secret, tenant_id):
        """
        Télécharge un fichier depuis SharePoint en utilisant l'API Microsoft Graph
        Retourne le contenu du fichier en bytes
        """
        try:
            from office365.sharepoint.client_context import ClientContext
            from office365.runtime.auth.client_credential import ClientCredential
        except ImportError:
            self.log_and_print(
                "❌ Package 'Office365-REST-Python-Client' non installé. "
                "Installez-le avec: pip install Office365-REST-Python-Client",
                level='error',
                style=self.style.ERROR
            )
            raise ImportError("Office365-REST-Python-Client requis")

        self.log_and_print(f"📡 Connexion à SharePoint: {site_url}")
        logger.debug(f"File path: {file_path}")

        # Authentification
        credentials = ClientCredential(client_id, client_secret)
        ctx = ClientContext(site_url).with_credentials(credentials)

        # Téléchargement du fichier
        self.log_and_print(f"📥 Téléchargement: {file_path}")
        
        file_content = io.BytesIO()
        file_url = f"/sites/{site_url.split('/sites/')[-1]}/{file_path}"
        
        try:
            ctx.web.get_file_by_server_relative_url(file_path).download(file_content).execute_query()
            file_content.seek(0)
            self.log_and_print("✅ Fichier téléchargé avec succès", style=self.style.SUCCESS)
            return file_content
        except Exception as e:
            self.log_and_print(f"❌ Erreur téléchargement: {e}", level='error', style=self.style.ERROR)
            raise

    def get_last_date_in_db(self, vl_model):
        """Récupère la dernière date en base pour un modèle VL"""
        last_vl = vl_model.objects.order_by('-date').first()
        return last_vl.date if last_vl else None

    def handle(self, *args, **options):
        start_time = datetime.now()
        self.log_and_print(f"\n{'='*60}")
        self.log_and_print(f"🚀 SYNCHRONISATION VL - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_and_print(f"{'='*60}\n")

        # Récupération des credentials
        client_id = options.get('client_id') or os.environ.get('SHAREPOINT_CLIENT_ID')
        client_secret = options.get('client_secret') or os.environ.get('SHAREPOINT_CLIENT_SECRET')
        tenant_id = options.get('tenant_id') or os.environ.get('SHAREPOINT_TENANT_ID')

        dry_run = options['dry_run']
        if dry_run:
            self.log_and_print("⚠️  MODE SIMULATION (dry-run) - Aucune modification ne sera effectuée\n", 
                            style=self.style.WARNING)

        # =====================================================================
        # ÉTAPE 1: Connexion et téléchargement depuis SharePoint
        # =====================================================================
        self.log_and_print("📋 ÉTAPE 1: Récupération du fichier Excel")
        self.log_and_print("-" * 40)

        if options.get('local_file'):
            # Mode local pour tests
            local_path = options['local_file']
            self.log_and_print(f"📂 Mode local: {local_path}")
            try:
                file_content = open(local_path, 'rb')
            except FileNotFoundError:
                self.log_and_print(f"❌ Fichier non trouvé: {local_path}", level='error', style=self.style.ERROR)
                return
        else:
            # Mode SharePoint
            if not all([client_id, client_secret, tenant_id]):
                self.log_and_print(
                    "❌ Credentials SharePoint manquants. Fournissez --client-id, --client-secret, --tenant-id "
                    "ou définissez les variables d'environnement SHAREPOINT_CLIENT_ID, SHAREPOINT_CLIENT_SECRET, SHAREPOINT_TENANT_ID",
                    level='error',
                    style=self.style.ERROR
                )
                return

            try:
                file_content = self.download_from_sharepoint(
                    options['site_url'],
                    options['file_path'],
                    client_id,
                    client_secret,
                    tenant_id
                )
            except Exception as e:
                self.log_and_print(f"❌ Échec connexion SharePoint: {e}", level='error', style=self.style.ERROR)
                return

        # =====================================================================
        # ÉTAPE 2: Lecture du fichier Excel
        # =====================================================================
        self.log_and_print(f"\n📋 ÉTAPE 2: Lecture du fichier Excel (feuille: {options['sheet_name']})")
        self.log_and_print("-" * 40)

        try:
            df = pd.read_excel(file_content, sheet_name=options['sheet_name'])
            self.log_and_print(f"✅ Fichier lu: {len(df)} lignes, {len(df.columns)} colonnes", style=self.style.SUCCESS)
            logger.debug(f"Colonnes: {list(df.columns)}")
        except Exception as e:
            self.log_and_print(f"❌ Erreur lecture Excel: {e}", level='error', style=self.style.ERROR)
            return
        finally:
            if hasattr(file_content, 'close'):
                file_content.close()

        # Vérifier la présence de la colonne Date
        if 'Date' not in df.columns:
            self.log_and_print("❌ Colonne 'Date' non trouvée dans le fichier", level='error', style=self.style.ERROR)
            return

        # =====================================================================
        # ÉTAPE 3: Connexion à la base et récupération des FCP
        # =====================================================================
        self.log_and_print(f"\n📋 ÉTAPE 3: Préparation de la base de données")
        self.log_and_print("-" * 40)

        fcp_dict = {fcp.nom: fcp for fcp in FicheSignaletique.objects.all()}
        self.log_and_print(f"📊 {len(fcp_dict)} FCP trouvés en base")

        # Colonnes FCP (toutes sauf Date)
        fcp_columns = [col for col in df.columns if col != 'Date']
        self.log_and_print(f"📊 {len(fcp_columns)} colonnes FCP dans le fichier Excel")

        # =====================================================================
        # ÉTAPE 4: Insertion incrémentale
        # =====================================================================
        self.log_and_print(f"\n📋 ÉTAPE 4: Insertion incrémentale des VL")
        self.log_and_print("-" * 40)

        total_inserted = 0
        total_skipped = 0
        fcp_stats = []

        for fcp_name in fcp_columns:
            # Récupérer le modèle VL correspondant
            vl_model = get_vl_model(fcp_name)

            if vl_model is None:
                self.log_and_print(f"  ⚠️  Modèle non trouvé: {fcp_name}", level='warning', style=self.style.WARNING)
                continue

            # Récupérer l'objet FCP
            fcp_obj = fcp_dict.get(fcp_name)
            if fcp_obj is None:
                self.log_and_print(f"  ⚠️  FCP non trouvé en base: {fcp_name}", level='warning', style=self.style.WARNING)
                continue

            # Récupérer la dernière date en base
            last_date = self.get_last_date_in_db(vl_model)
            if last_date:
                logger.debug(f"{fcp_name}: dernière date en base = {last_date}")

            # Préparer les objets VL à insérer (uniquement nouvelles dates)
            vl_objects = []
            skipped_count = 0

            for idx, row in df.iterrows():
                date_val = row['Date']
                valeur = row[fcp_name]

                # Ignorer les valeurs nulles
                if pd.isna(date_val) or pd.isna(valeur):
                    continue

                # Convertir la date
                if isinstance(date_val, datetime):
                    date = date_val.date()
                elif isinstance(date_val, pd.Timestamp):
                    date = date_val.date()
                elif isinstance(date_val, str):
                    date = datetime.strptime(date_val, '%Y-%m-%d').date()
                else:
                    date = date_val

                # Vérifier si la date est plus récente que la dernière en base
                if last_date and date <= last_date:
                    skipped_count += 1
                    continue

                vl_objects.append(vl_model(
                    fcp=fcp_obj,
                    date=date,
                    valeur=Decimal(str(valeur))
                ))

            # Insertion en base
            if vl_objects:
                if not dry_run:
                    # Utiliser bulk_create avec ignore_conflicts pour éviter les doublons
                    vl_model.objects.bulk_create(vl_objects, ignore_conflicts=True)
                
                self.log_and_print(
                    f"  ✅ {fcp_name}: +{len(vl_objects)} VL (dernière date base: {last_date or 'aucune'})",
                    style=self.style.SUCCESS
                )
                total_inserted += len(vl_objects)
                fcp_stats.append({
                    'fcp': fcp_name,
                    'inserted': len(vl_objects),
                    'skipped': skipped_count,
                    'last_date_before': last_date
                })
            else:
                if skipped_count > 0:
                    self.log_and_print(f"  ⏭️  {fcp_name}: 0 nouvelle VL ({skipped_count} déjà en base)")
                else:
                    self.log_and_print(f"  ➖ {fcp_name}: aucune donnée valide")
                total_skipped += skipped_count

        # =====================================================================
        # RÉSUMÉ
        # =====================================================================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.log_and_print(f"\n{'='*60}")
        self.log_and_print(f"📊 RÉSUMÉ DE LA SYNCHRONISATION")
        self.log_and_print(f"{'='*60}")
        self.log_and_print(f"  ⏱️  Durée: {duration:.2f} secondes")
        self.log_and_print(f"  ✅ VL insérées: {total_inserted}", style=self.style.SUCCESS if total_inserted > 0 else None)
        self.log_and_print(f"  ⏭️  VL ignorées (déjà en base): {total_skipped}")
        self.log_and_print(f"  📁 Log détaillé: {LOG_DIR / 'sync_vl_sharepoint.log'}")

        if dry_run:
            self.log_and_print(f"\n⚠️  MODE SIMULATION - Aucune donnée n'a été insérée", style=self.style.WARNING)

        self.log_and_print(f"\n{'='*60}\n")

        # Log du résumé
        logger.info(f"Synchronisation terminée - {total_inserted} insérées, {total_skipped} ignorées, durée: {duration:.2f}s")
