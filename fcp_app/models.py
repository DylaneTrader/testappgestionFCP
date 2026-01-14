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


class ValeurLiquidative(models.Model):
    """
    Table des valeurs liquidatives (séries temporelles)
    """
    fcp = models.ForeignKey(
        FicheSignaletique, 
        on_delete=models.CASCADE, 
        related_name='valeurs_liquidatives',
        verbose_name="FCP"
    )
    date = models.DateField(verbose_name="Date")
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
        verbose_name = "Valeur Liquidative"
        verbose_name_plural = "Valeurs Liquidatives"
        ordering = ['-date', 'fcp']
        unique_together = ['fcp', 'date']  # Une seule VL par FCP et par date
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.date} : {self.valeur}"
