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
        ('Capital-Risque', 'Capital-Risque'),
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


# ============================================================================
# Tables de Composition des FCP - Poches et Instruments
# ============================================================================

class TypePoche(models.TextChoices):
    """Types de poches disponibles pour la composition d'un FCP"""
    ACTION = 'ACTION', 'Action'
    OBLIGATION = 'OBLIGATION', 'Obligation'
    LIQUIDITE = 'LIQUIDITE', 'Liquidité'
    FCP = 'FCP', 'FCP'


class CompositionPoche(models.Model):
    """
    Table de composition d'un FCP par poche.
    Chaque FCP peut avoir jusqu'à 4 poches (Action, Obligation, Liquidité, FCP).
    """
    fcp = models.ForeignKey(
        FicheSignaletique, 
        on_delete=models.CASCADE, 
        related_name='poches',
        verbose_name="FCP"
    )
    type_poche = models.CharField(
        max_length=20,
        choices=TypePoche.choices,
        verbose_name="Type de poche"
    )
    date_composition = models.DateField(verbose_name="Date de composition")
    poids_poche = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name="Poids de la poche (%)",
        help_text="Pourcentage du total de l'actif"
    )
    montant = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Montant (XOF)"
    )
    
    class Meta:
        verbose_name = "Composition - Poche"
        verbose_name_plural = "Compositions - Poches"
        ordering = ['fcp', 'date_composition', 'type_poche']
        unique_together = ['fcp', 'type_poche', 'date_composition']
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.get_type_poche_display()} ({self.date_composition})"


class BaseInstrument(models.Model):
    """
    Classe abstraite de base pour tous les instruments d'une poche.
    """
    poche = models.ForeignKey(
        CompositionPoche, 
        on_delete=models.CASCADE, 
        related_name='%(class)s_instruments',
        verbose_name="Poche"
    )
    nom = models.CharField(max_length=200, verbose_name="Nom de l'instrument")
    code_isin = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name="Code ISIN"
    )
    quantite = models.DecimalField(
        max_digits=18, 
        decimal_places=4, 
        null=True, 
        blank=True, 
        verbose_name="Quantité"
    )
    prix_unitaire = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        null=True, 
        blank=True, 
        verbose_name="Prix unitaire"
    )
    valorisation = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        verbose_name="Valorisation (XOF)"
    )
    poids = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        verbose_name="Poids (%)",
        help_text="Pourcentage dans la poche"
    )
    
    class Meta:
        abstract = True
        ordering = ['-poids']
    
    def __str__(self):
        return f"{self.nom} - {self.poids}%"


class InstrumentAction(BaseInstrument):
    """
    Instrument de type Action (titres de capital cotés BRVM).
    """
    secteur = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Secteur d'activité"
    )
    ticker = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name="Ticker BRVM"
    )
    pays = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="Pays"
    )
    
    class Meta(BaseInstrument.Meta):
        verbose_name = "Instrument - Action"
        verbose_name_plural = "Instruments - Actions"
        db_table = 'fcp_app_instrument_action'


class InstrumentObligation(BaseInstrument):
    """
    Instrument de type Obligation (titres de créance).
    """
    TYPE_OBLIGATION_CHOICES = [
        ('ETAT', 'Obligation d\'État'),
        ('CORPORATE', 'Obligation Corporate'),
        ('TRESOR', 'Bon du Trésor'),
        ('AUTRE', 'Autre'),
    ]
    
    type_obligation = models.CharField(
        max_length=20,
        choices=TYPE_OBLIGATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Type d'obligation"
    )
    emetteur = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="Émetteur"
    )
    taux_nominal = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        null=True, 
        blank=True, 
        verbose_name="Taux nominal (%)"
    )
    date_echeance = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Date d'échéance"
    )
    maturite_residuelle = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Maturité résiduelle (années)"
    )
    
    class Meta(BaseInstrument.Meta):
        verbose_name = "Instrument - Obligation"
        verbose_name_plural = "Instruments - Obligations"
        db_table = 'fcp_app_instrument_obligation'


class InstrumentLiquidite(BaseInstrument):
    """
    Instrument de type Liquidité (dépôts, comptes courants, placements monétaires).
    """
    TYPE_LIQUIDITE_CHOICES = [
        ('DAT', 'Dépôt à Terme'),
        ('COMPTE_COURANT', 'Compte Courant'),
        ('DAV', 'Dépôt à Vue'),
        ('PENSION', 'Mise en Pension'),
        ('AUTRE', 'Autre'),
    ]
    
    type_liquidite = models.CharField(
        max_length=20,
        choices=TYPE_LIQUIDITE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Type de liquidité"
    )
    etablissement = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="Établissement"
    )
    taux = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        null=True, 
        blank=True, 
        verbose_name="Taux de rémunération (%)"
    )
    date_echeance = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Date d'échéance"
    )
    
    class Meta(BaseInstrument.Meta):
        verbose_name = "Instrument - Liquidité"
        verbose_name_plural = "Instruments - Liquidités"
        db_table = 'fcp_app_instrument_liquidite'


class InstrumentFCP(BaseInstrument):
    """
    Instrument de type FCP (investissement dans d'autres FCP/OPCVM).
    """
    fcp_cible = models.ForeignKey(
        FicheSignaletique,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investissements_recus',
        verbose_name="FCP cible (si géré par CGF)"
    )
    gestionnaire = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="Gestionnaire du FCP"
    )
    type_fcp = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="Type de FCP",
        help_text="Diversifié, Obligataire, Actions, Monétaire"
    )
    vl_souscription = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        null=True, 
        blank=True, 
        verbose_name="VL de souscription"
    )
    
    class Meta(BaseInstrument.Meta):
        verbose_name = "Instrument - FCP"
        verbose_name_plural = "Instruments - FCP"
        db_table = 'fcp_app_instrument_fcp'


# ============================================================================
# Tables de Séries de Benchmarks
# ============================================================================

class BaseBenchmark(models.Model):
    """
    Classe abstraite de base pour les tables de benchmarks.
    """
    date = models.DateField(verbose_name="Date", unique=True)
    valeur = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name="Valeur de l'indice"
    )
    variation_journaliere = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Variation journalière (%)"
    )
    
    class Meta:
        abstract = True
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date}: {self.valeur}"


class BenchmarkObligation(BaseBenchmark):
    """
    Table des séries temporelles du benchmark obligataire.
    """
    class Meta(BaseBenchmark.Meta):
        verbose_name = "Benchmark Obligataire"
        verbose_name_plural = "Benchmarks Obligataires"
        db_table = 'fcp_app_benchmark_obligation'


class BenchmarkBRVM(BaseBenchmark):
    """
    Table des séries temporelles du benchmark actions (BRVM Composite).
    """
    class Meta(BaseBenchmark.Meta):
        verbose_name = "Benchmark BRVM"
        verbose_name_plural = "Benchmarks BRVM"
        db_table = 'fcp_app_benchmark_brvm'


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

