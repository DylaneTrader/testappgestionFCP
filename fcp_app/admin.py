from django.contrib import admin
from .models import (
    FicheSignaletique, FCP_VL_MODELS, BenchmarkObligation, BenchmarkBRVM,
    VL_FCP_Actions_Pharmacie, VL_FCP_Al_Baraka_2, VL_FCP_Assur_Senegal,
    VL_FCP_BNDE_Valeurs, VL_FCP_Capital_Retraite, VL_FCP_Diaspora,
    VL_FCP_Djolof, VL_FCP_Expat, VL_FCP_IFC_BOAD, VL_FCP_Liquidite_Optimum,
    VL_FCP_Placement_Avantage, VL_FCP_Placement_Croissance, VL_FCP_Placement_Quietude,
    VL_FCP_Postefinances, VL_FCP_Rente_Perpetuelle, VL_FCP_Salam_CI,
    VL_FCP_Transvie, VL_FCP_UCA_Doguicimi, VL_FCP_Vision_Monetaire,
    VL_FCP_Walo, VL_FCPCR_Sonatel, VL_FCPE_DP_World_Dakar,
    VL_FCPE_Force_PAD, VL_FCPE_Sini_Gnesigui, VL_FCPR_SenFonds,
    # Modèles de composition
    CompositionPoche, InstrumentAction, InstrumentObligation,
    InstrumentLiquidite, InstrumentFCP
)


@admin.register(FicheSignaletique)
class FicheSignaletiqueAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_fond', 'echelle_risque', 'horizon', 'benchmark_oblig', 'benchmark_brvmc', 'devise', 'actif']
    list_filter = ['type_fond', 'echelle_risque', 'gestionnaire', 'actif']
    search_fields = ['nom', 'description']
    ordering = ['nom']


# Admin générique pour les tables VL
class BaseVLAdmin(admin.ModelAdmin):
    list_display = ['date', 'valeur', 'actif_net', 'nombre_parts']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date']
    date_hierarchy = 'date'


# Enregistrement de toutes les tables VL
admin.site.register(VL_FCP_Actions_Pharmacie, BaseVLAdmin)
admin.site.register(VL_FCP_Al_Baraka_2, BaseVLAdmin)
admin.site.register(VL_FCP_Assur_Senegal, BaseVLAdmin)
admin.site.register(VL_FCP_BNDE_Valeurs, BaseVLAdmin)
admin.site.register(VL_FCP_Capital_Retraite, BaseVLAdmin)
admin.site.register(VL_FCP_Diaspora, BaseVLAdmin)
admin.site.register(VL_FCP_Djolof, BaseVLAdmin)
admin.site.register(VL_FCP_Expat, BaseVLAdmin)
admin.site.register(VL_FCP_IFC_BOAD, BaseVLAdmin)
admin.site.register(VL_FCP_Liquidite_Optimum, BaseVLAdmin)
admin.site.register(VL_FCP_Placement_Avantage, BaseVLAdmin)
admin.site.register(VL_FCP_Placement_Croissance, BaseVLAdmin)
admin.site.register(VL_FCP_Placement_Quietude, BaseVLAdmin)
admin.site.register(VL_FCP_Postefinances, BaseVLAdmin)
admin.site.register(VL_FCP_Rente_Perpetuelle, BaseVLAdmin)
admin.site.register(VL_FCP_Salam_CI, BaseVLAdmin)
admin.site.register(VL_FCP_Transvie, BaseVLAdmin)
admin.site.register(VL_FCP_UCA_Doguicimi, BaseVLAdmin)
admin.site.register(VL_FCP_Vision_Monetaire, BaseVLAdmin)
admin.site.register(VL_FCP_Walo, BaseVLAdmin)
admin.site.register(VL_FCPCR_Sonatel, BaseVLAdmin)
admin.site.register(VL_FCPE_DP_World_Dakar, BaseVLAdmin)
admin.site.register(VL_FCPE_Force_PAD, BaseVLAdmin)
admin.site.register(VL_FCPE_Sini_Gnesigui, BaseVLAdmin)
admin.site.register(VL_FCPR_SenFonds, BaseVLAdmin)


# Admin pour les séries de benchmarks
class BaseBenchmarkAdmin(admin.ModelAdmin):
    list_display = ['date', 'valeur', 'variation_journaliere']
    list_filter = ['date']
    search_fields = ['date']
    ordering = ['-date']
    date_hierarchy = 'date'


admin.site.register(BenchmarkObligation, BaseBenchmarkAdmin)
admin.site.register(BenchmarkBRVM, BaseBenchmarkAdmin)


# ============================================================================
# Admin pour la Composition des FCP
# ============================================================================

class InstrumentActionInline(admin.TabularInline):
    model = InstrumentAction
    extra = 0
    fields = ['nom', 'ticker', 'code_isin', 'quantite', 'prix_unitaire', 'valorisation', 'poids', 'secteur', 'pays']


class InstrumentObligationInline(admin.TabularInline):
    model = InstrumentObligation
    extra = 0
    fields = ['nom', 'code_isin', 'emetteur', 'type_obligation', 'taux_nominal', 'date_echeance', 'valorisation', 'poids']


class InstrumentLiquiditeInline(admin.TabularInline):
    model = InstrumentLiquidite
    extra = 0
    fields = ['nom', 'etablissement', 'type_liquidite', 'taux', 'date_echeance', 'valorisation', 'poids']


class InstrumentFCPInline(admin.TabularInline):
    model = InstrumentFCP
    extra = 0
    fields = ['nom', 'fcp_cible', 'gestionnaire', 'type_fcp', 'quantite', 'vl_souscription', 'valorisation', 'poids']


@admin.register(CompositionPoche)
class CompositionPocheAdmin(admin.ModelAdmin):
    list_display = ['fcp', 'type_poche', 'date_composition', 'poids_poche', 'montant']
    list_filter = ['type_poche', 'fcp', 'date_composition']
    search_fields = ['fcp__nom']
    ordering = ['-date_composition', 'fcp', 'type_poche']
    date_hierarchy = 'date_composition'
    inlines = [InstrumentActionInline, InstrumentObligationInline, InstrumentLiquiditeInline, InstrumentFCPInline]
    
    def get_inlines(self, request, obj):
        """Affiche uniquement les inlines pertinents selon le type de poche"""
        if obj is None:
            return []
        if obj.type_poche == 'ACTION':
            return [InstrumentActionInline]
        elif obj.type_poche == 'OBLIGATION':
            return [InstrumentObligationInline]
        elif obj.type_poche == 'LIQUIDITE':
            return [InstrumentLiquiditeInline]
        elif obj.type_poche == 'FCP':
            return [InstrumentFCPInline]
        return []


@admin.register(InstrumentAction)
class InstrumentActionAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ticker', 'poche', 'quantite', 'prix_unitaire', 'valorisation', 'poids', 'secteur']
    list_filter = ['poche__fcp', 'secteur', 'pays']
    search_fields = ['nom', 'ticker', 'code_isin']
    ordering = ['-poids']


@admin.register(InstrumentObligation)
class InstrumentObligationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'poche', 'type_obligation', 'emetteur', 'taux_nominal', 'date_echeance', 'valorisation', 'poids']
    list_filter = ['poche__fcp', 'type_obligation', 'emetteur']
    search_fields = ['nom', 'code_isin', 'emetteur']
    ordering = ['-poids']


@admin.register(InstrumentLiquidite)
class InstrumentLiquiditeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'poche', 'type_liquidite', 'etablissement', 'taux', 'valorisation', 'poids']
    list_filter = ['poche__fcp', 'type_liquidite', 'etablissement']
    search_fields = ['nom', 'etablissement']
    ordering = ['-poids']


@admin.register(InstrumentFCP)
class InstrumentFCPAdmin(admin.ModelAdmin):
    list_display = ['nom', 'poche', 'fcp_cible', 'gestionnaire', 'type_fcp', 'valorisation', 'poids']
    list_filter = ['poche__fcp', 'gestionnaire', 'type_fcp']
    search_fields = ['nom', 'gestionnaire']
    ordering = ['-poids']
