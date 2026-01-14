from django.db import models

# Modèles pour la gestion des FCP


class FicheSignaletique(models.Model):
    """
    Table des fiches signalétiques des FCP
    """
    TYPE_FOND_CHOICES = [
        ('Diversifié', 'Diversifié'),
        ('Obligataire', 'Obligataire'),
        ('Actions', 'Actions'),
        ('Monétaire', 'Monétaire'),
    ]
    
    ECHELLE_RISQUE_CHOICES = [(i, str(i)) for i in range(1, 8)]
    
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du FCP")
    echelle_risque = models.IntegerField(
        choices=ECHELLE_RISQUE_CHOICES, 
        verbose_name="Échelle de risque (1-7)"
    )
    type_fond = models.CharField(
        max_length=20, 
        choices=TYPE_FOND_CHOICES, 
        verbose_name="Type de fond"
    )
    horizon = models.IntegerField(verbose_name="Horizon d'investissement (années)")
    benchmark_oblig = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Benchmark Obligataire (%)"
    )
    benchmark_brvmc = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Benchmark BRVM C (%)"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    devise = models.CharField(max_length=10, default="XOF", verbose_name="Devise")
    gestionnaire = models.CharField(max_length=100, default="CGF Bourse", verbose_name="Gestionnaire")
    date_creation = models.DateField(null=True, blank=True, verbose_name="Date de création")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Fiche Signalétique"
        verbose_name_plural = "Fiches Signalétiques"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    
    @property
    def risk_label(self):
        """Retourne le libellé du niveau de risque"""
        labels = {
            1: "Très faible",
            2: "Faible", 
            3: "Modéré",
            4: "Moyen",
            5: "Élevé",
            6: "Très élevé",
            7: "Maximum"
        }
        return labels.get(self.echelle_risque, "")
    
    @property
    def type_icon(self):
        """Retourne l'icône Bootstrap pour le type de fond"""
        icons = {
            "Diversifié": "bi bi-pie-chart-fill",
            "Obligataire": "bi bi-bank",
            "Actions": "bi bi-graph-up-arrow",
            "Monétaire": "bi bi-cash-coin"
        }
        return icons.get(self.type_fond, "bi bi-question-circle")
    
    @property
    def type_color(self):
        """Retourne la couleur pour le type de fond"""
        colors = {
            "Diversifié": "#004080",
            "Obligataire": "#28a745",
            "Actions": "#dc3545",
            "Monétaire": "#ffc107"
        }
        return colors.get(self.type_fond, "#6c757d")


# ============================================================================
# Tables de Valeurs Liquidatives - Une table par FCP
# ============================================================================

class BaseValeurLiquidative(models.Model):
    """
    Classe abstraite de base pour toutes les tables de valeurs liquidatives
    """
    date = models.DateField(verbose_name="Date", unique=True)
    valeur = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        verbose_name="Valeur Liquidative"
    )
    actif_net = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Actif Net"
    )
    nombre_parts = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        null=True, 
        blank=True, 
        verbose_name="Nombre de parts"
    )
    
    class Meta:
        abstract = True
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} : {self.valeur}"


class VL_FCP_Actions_Pharmacie(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_actions_pharmacie', default=1)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Actions Pharmacie"
        verbose_name_plural = "VL FCP Actions Pharmacie"
        db_table = 'fcp_app_vl_actions_pharmacie'


class VL_FCP_Al_Baraka_2(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_al_baraka_2', default=2)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Al Baraka 2"
        verbose_name_plural = "VL FCP Al Baraka 2"
        db_table = 'fcp_app_vl_al_baraka_2'


class VL_FCP_Assur_Senegal(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_assur_senegal', default=3)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Assur Senegal"
        verbose_name_plural = "VL FCP Assur Senegal"
        db_table = 'fcp_app_vl_assur_senegal'


class VL_FCP_BNDE_Valeurs(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_bnde_valeurs', default=4)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP BNDE Valeurs"
        verbose_name_plural = "VL FCP BNDE Valeurs"
        db_table = 'fcp_app_vl_bnde_valeurs'


class VL_FCP_Capital_Retraite(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_capital_retraite', default=5)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Capital Retraite"
        verbose_name_plural = "VL FCP Capital Retraite"
        db_table = 'fcp_app_vl_capital_retraite'


class VL_FCP_Diaspora(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_diaspora', default=6)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Diaspora"
        verbose_name_plural = "VL FCP Diaspora"
        db_table = 'fcp_app_vl_diaspora'


class VL_FCP_Djolof(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_djolof', default=7)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Djolof"
        verbose_name_plural = "VL FCP Djolof"
        db_table = 'fcp_app_vl_djolof'


class VL_FCP_Expat(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_expat', default=8)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Expat"
        verbose_name_plural = "VL FCP Expat"
        db_table = 'fcp_app_vl_expat'


class VL_FCP_IFC_BOAD(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_ifc_boad', default=9)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP IFC-BOAD"
        verbose_name_plural = "VL FCP IFC-BOAD"
        db_table = 'fcp_app_vl_ifc_boad'


class VL_FCP_Liquidite_Optimum(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_liquidite_optimum', default=10)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Liquidité Optimum"
        verbose_name_plural = "VL FCP Liquidité Optimum"
        db_table = 'fcp_app_vl_liquidite_optimum'


class VL_FCP_Placement_Avantage(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_placement_avantage', default=11)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Placement Avantage"
        verbose_name_plural = "VL FCP Placement Avantage"
        db_table = 'fcp_app_vl_placement_avantage'


class VL_FCP_Placement_Croissance(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_placement_croissance', default=12)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Placement Croissance"
        verbose_name_plural = "VL FCP Placement Croissance"
        db_table = 'fcp_app_vl_placement_croissance'


class VL_FCP_Placement_Quietude(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_placement_quietude', default=13)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Placement Quiétude"
        verbose_name_plural = "VL FCP Placement Quiétude"
        db_table = 'fcp_app_vl_placement_quietude'


class VL_FCP_Postefinances(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_postefinances', default=14)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Postefinances"
        verbose_name_plural = "VL FCP Postefinances"
        db_table = 'fcp_app_vl_postefinances'


class VL_FCP_Rente_Perpetuelle(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_rente_perpetuelle', default=15)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Rente Perpétuelle"
        verbose_name_plural = "VL FCP Rente Perpétuelle"
        db_table = 'fcp_app_vl_rente_perpetuelle'


class VL_FCP_Salam_CI(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_salam_ci', default=16)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Salam CI"
        verbose_name_plural = "VL FCP Salam CI"
        db_table = 'fcp_app_vl_salam_ci'


class VL_FCP_Transvie(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_transvie', default=17)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Transvie"
        verbose_name_plural = "VL FCP Transvie"
        db_table = 'fcp_app_vl_transvie'


class VL_FCP_UCA_Doguicimi(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_uca_doguicimi', default=18)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP UCA Doguicimi"
        verbose_name_plural = "VL FCP UCA Doguicimi"
        db_table = 'fcp_app_vl_uca_doguicimi'


class VL_FCP_Vision_Monetaire(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_vision_monetaire', default=19)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Vision Monétaire"
        verbose_name_plural = "VL FCP Vision Monétaire"
        db_table = 'fcp_app_vl_vision_monetaire'


class VL_FCP_Walo(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_walo', default=20)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCP Walo"
        verbose_name_plural = "VL FCP Walo"
        db_table = 'fcp_app_vl_walo'


class VL_FCPCR_Sonatel(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_sonatel', default=21)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCPCR Sonatel"
        verbose_name_plural = "VL FCPCR Sonatel"
        db_table = 'fcp_app_vl_sonatel'


class VL_FCPE_DP_World_Dakar(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_dp_world_dakar', default=22)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCPE DP World Dakar"
        verbose_name_plural = "VL FCPE DP World Dakar"
        db_table = 'fcp_app_vl_dp_world_dakar'


class VL_FCPE_Force_PAD(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_force_pad', default=23)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCPE Force PAD"
        verbose_name_plural = "VL FCPE Force PAD"
        db_table = 'fcp_app_vl_force_pad'


class VL_FCPE_Sini_Gnesigui(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_sini_gnesigui', default=24)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCPE Sini Gnesigui"
        verbose_name_plural = "VL FCPE Sini Gnesigui"
        db_table = 'fcp_app_vl_sini_gnesigui'


class VL_FCPR_SenFonds(BaseValeurLiquidative):
    fcp = models.ForeignKey(FicheSignaletique, on_delete=models.CASCADE, related_name='vl_senfonds', default=25)
    class Meta(BaseValeurLiquidative.Meta):
        verbose_name = "VL FCPR Sen'Fonds"
        verbose_name_plural = "VL FCPR Sen'Fonds"
        db_table = 'fcp_app_vl_senfonds'


# Dictionnaire de mapping nom FCP -> modèle VL
FCP_VL_MODELS = {
    "FCP ACTIONS PHARMACIE": VL_FCP_Actions_Pharmacie,
    "FCP AL BARAKA 2": VL_FCP_Al_Baraka_2,
    "FCP ASSUR SENEGAL": VL_FCP_Assur_Senegal,
    "FCP BNDE VALEURS": VL_FCP_BNDE_Valeurs,
    "FCP CAPITAL RETRAITE": VL_FCP_Capital_Retraite,
    "FCP DIASPORA": VL_FCP_Diaspora,
    "FCP DJOLOF": VL_FCP_Djolof,
    "FCP EXPAT": VL_FCP_Expat,
    "FCP IFC-BOAD": VL_FCP_IFC_BOAD,
    "FCP LIQUIDITE OPTIMUM": VL_FCP_Liquidite_Optimum,
    "FCP PLACEMENT AVANTAGE": VL_FCP_Placement_Avantage,
    "FCP PLACEMENT CROISSANCE": VL_FCP_Placement_Croissance,
    "FCP PLACEMENT QUIETUDE": VL_FCP_Placement_Quietude,
    "FCP POSTEFINANCES": VL_FCP_Postefinances,
    "FCP RENTE PERPETUELLE": VL_FCP_Rente_Perpetuelle,
    "FCP SALAM CI": VL_FCP_Salam_CI,
    "FCP TRANSVIE": VL_FCP_Transvie,
    "FCP UCA DOGUICIMI": VL_FCP_UCA_Doguicimi,
    "FCP VISION MONETAIRE": VL_FCP_Vision_Monetaire,
    "FCP WALO": VL_FCP_Walo,
    "FCPCR SONATEL": VL_FCPCR_Sonatel,
    "FCPE DP WORLD DAKAR": VL_FCPE_DP_World_Dakar,
    "FCPE FORCE PAD": VL_FCPE_Force_PAD,
    "FCPE SINI GNESIGUI": VL_FCPE_Sini_Gnesigui,
    "FCPR SEN'FONDS": VL_FCPR_SenFonds,
}


def get_vl_model(fcp_name):
    """Retourne le modèle VL correspondant au nom du FCP"""
    return FCP_VL_MODELS.get(fcp_name)

