from django.contrib import admin
from .models import (
    FCP, ValeurLiquidative, TypeClient, TypeOperation, SouscriptionRachat,
    ActifNet, TypeFCP, ClasseActif, Secteur, Pays, SecteurObligation,
    Cotation, CompositionFCP, Benchmark, PoidsQuotidien
)


@admin.register(FCP)
class FCPAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation', 'actif']
    list_filter = ['actif']
    search_fields = ['nom']
    ordering = ['nom']


@admin.register(ValeurLiquidative)
class ValeurLiquidativeAdmin(admin.ModelAdmin):
    list_display = ['fcp', 'date', 'valeur']
    list_filter = ['fcp', 'date']
    search_fields = ['fcp__nom']
    date_hierarchy = 'date'
    ordering = ['-date', 'fcp']


@admin.register(TypeClient)
class TypeClientAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(TypeOperation)
class TypeOperationAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(SouscriptionRachat)
class SouscriptionRachatAdmin(admin.ModelAdmin):
    list_display = ['date', 'fcp', 'type_operation', 'type_client', 'montant']
    list_filter = ['type_operation', 'type_client', 'fcp', 'date']
    search_fields = ['fcp__nom']
    date_hierarchy = 'date'
    ordering = ['-date']


@admin.register(ActifNet)
class ActifNetAdmin(admin.ModelAdmin):
    list_display = ['fcp', 'date', 'montant']
    list_filter = ['fcp', 'date']
    search_fields = ['fcp__nom']
    date_hierarchy = 'date'
    ordering = ['-date', 'fcp']


@admin.register(TypeFCP)
class TypeFCPAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(ClasseActif)
class ClasseActifAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Secteur)
class SecteurAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code']
    search_fields = ['nom', 'code']


@admin.register(SecteurObligation)
class SecteurObligationAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(Cotation)
class CotationAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']


@admin.register(CompositionFCP)
class CompositionFCPAdmin(admin.ModelAdmin):
    list_display = ['fcp', 'type_fcp', 'classe', 'secteur', 'pays', 'pourcentage']
    list_filter = ['fcp', 'type_fcp', 'classe', 'secteur', 'pays']
    search_fields = ['fcp__nom']
    ordering = ['fcp', '-pourcentage']


@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = ['date', 'benchmark_obligataire', 'benchmark_actions']
    date_hierarchy = 'date'
    ordering = ['-date']


@admin.register(PoidsQuotidien)
class PoidsQuotidienAdmin(admin.ModelAdmin):
    list_display = ['fcp', 'date', 'actions', 'obligations', 'opcvm', 'liquidites']
    list_filter = ['fcp', 'date']
    search_fields = ['fcp__nom']
    date_hierarchy = 'date'
    ordering = ['-date', 'fcp']
