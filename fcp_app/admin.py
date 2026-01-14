from django.contrib import admin
from .models import FicheSignaletique, ValeurLiquidative


@admin.register(FicheSignaletique)
class FicheSignaletiqueAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_fond', 'echelle_risque', 'horizon', 'benchmark_oblig', 'benchmark_brvmc', 'devise', 'actif']
    list_filter = ['type_fond', 'echelle_risque', 'gestionnaire', 'actif']
    search_fields = ['nom', 'description']
    ordering = ['nom']


@admin.register(ValeurLiquidative)
class ValeurLiquidativeAdmin(admin.ModelAdmin):
    list_display = ['fcp', 'date', 'valeur', 'actif_net', 'nombre_parts']
    list_filter = ['fcp', 'date']
    search_fields = ['fcp__nom']
    ordering = ['-date', 'fcp']
    date_hierarchy = 'date'
