from django.contrib import admin
from .models import (
    FicheSignaletique, FCP_VL_MODELS,
    VL_FCP_Actions_Pharmacie, VL_FCP_Al_Baraka_2, VL_FCP_Assur_Senegal,
    VL_FCP_BNDE_Valeurs, VL_FCP_Capital_Retraite, VL_FCP_Diaspora,
    VL_FCP_Djolof, VL_FCP_Expat, VL_FCP_IFC_BOAD, VL_FCP_Liquidite_Optimum,
    VL_FCP_Placement_Avantage, VL_FCP_Placement_Croissance, VL_FCP_Placement_Quietude,
    VL_FCP_Postefinances, VL_FCP_Rente_Perpetuelle, VL_FCP_Salam_CI,
    VL_FCP_Transvie, VL_FCP_UCA_Doguicimi, VL_FCP_Vision_Monetaire,
    VL_FCP_Walo, VL_FCPCR_Sonatel, VL_FCPE_DP_World_Dakar,
    VL_FCPE_Force_PAD, VL_FCPE_Sini_Gnesigui, VL_FCPR_SenFonds
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
