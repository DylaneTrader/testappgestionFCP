"""
Commande Django pour peupler la table FicheSignaletique avec les données de data.py
"""
from django.core.management.base import BaseCommand
from fcp_app.models import FicheSignaletique
from fcp_app.data import FCP_FICHE_SIGNALETIQUE


class Command(BaseCommand):
    help = 'Peuple la table FicheSignaletique avec les données des FCP'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        
        for nom, data in FCP_FICHE_SIGNALETIQUE.items():
            fcp, created = FicheSignaletique.objects.update_or_create(
                nom=nom,
                defaults={
                    'echelle_risque': data['echelle_risque'],
                    'type_fond': data['type_fond'],
                    'horizon': data['horizon'],
                    'benchmark_oblig': data['benchmark_oblig'],
                    'benchmark_brvmc': data['benchmark_brvmc'],
                    'description': data.get('description', ''),
                    'devise': data.get('devise', 'XOF'),
                    'gestionnaire': data.get('gestionnaire', 'CGF Bourse'),
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Créé: {nom}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  ↻ Mis à jour: {nom}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Terminé! {created_count} FCP créés, {updated_count} mis à jour.'))
        self.stdout.write(self.style.SUCCESS(f'Total: {FicheSignaletique.objects.count()} FCP en base.'))
