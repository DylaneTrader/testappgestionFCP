from django.db import models
from django.core.validators import MinValueValidator


class FCP(models.Model):
    """Modèle représentant un Fonds Commun de Placement"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du FCP")
    date_creation = models.DateField(null=True, blank=True, verbose_name="Date de création")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "FCP"
        verbose_name_plural = "FCPs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class ValeurLiquidative(models.Model):
    """Valeurs liquidatives quotidiennes pour chaque FCP"""
    fcp = models.ForeignKey(FCP, on_delete=models.CASCADE, related_name='valeurs_liquidatives')
    date = models.DateField(verbose_name="Date")
    valeur = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name="Valeur liquidative"
    )
    
    class Meta:
        verbose_name = "Valeur Liquidative"
        verbose_name_plural = "Valeurs Liquidatives"
        ordering = ['-date', 'fcp']
        unique_together = ['fcp', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['fcp', 'date']),
        ]
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.date}: {self.valeur}"


class TypeClient(models.Model):
    """Types de clients (Particuliers, Personnes Morales, OPCVM, etc.)"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Type de client")
    
    class Meta:
        verbose_name = "Type de Client"
        verbose_name_plural = "Types de Clients"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class TypeOperation(models.Model):
    """Types d'opérations (Souscription, Rachat)"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Type d'opération")
    
    class Meta:
        verbose_name = "Type d'Opération"
        verbose_name_plural = "Types d'Opérations"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class SouscriptionRachat(models.Model):
    """Enregistrements des souscriptions et rachats"""
    date = models.DateField(verbose_name="Date")
    type_client = models.ForeignKey(
        TypeClient, 
        on_delete=models.PROTECT, 
        related_name='operations',
        verbose_name="Type de client"
    )
    type_operation = models.ForeignKey(
        TypeOperation, 
        on_delete=models.PROTECT, 
        related_name='operations',
        verbose_name="Type d'opération"
    )
    fcp = models.ForeignKey(
        FCP, 
        on_delete=models.CASCADE, 
        related_name='operations',
        verbose_name="FCP"
    )
    montant = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant"
    )
    
    class Meta:
        verbose_name = "Souscription/Rachat"
        verbose_name_plural = "Souscriptions/Rachats"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['fcp', 'date']),
            models.Index(fields=['type_operation', 'date']),
        ]
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.type_operation.nom} - {self.date}: {self.montant}"


class ActifNet(models.Model):
    """Actifs nets quotidiens pour chaque FCP"""
    fcp = models.ForeignKey(FCP, on_delete=models.CASCADE, related_name='actifs_nets')
    date = models.DateField(verbose_name="Date")
    montant = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Montant de l'actif net"
    )
    
    class Meta:
        verbose_name = "Actif Net"
        verbose_name_plural = "Actifs Nets"
        ordering = ['-date', 'fcp']
        unique_together = ['fcp', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['fcp', 'date']),
        ]
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.date}: {self.montant}"


class TypeFCP(models.Model):
    """Types de FCP (Actions, Obligataires, Monétaires)"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Type de FCP")
    
    class Meta:
        verbose_name = "Type de FCP"
        verbose_name_plural = "Types de FCP"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class ClasseActif(models.Model):
    """Classes d'actifs (Actions, Obligations, OPCVM, Liquidités)"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Classe d'actif")
    
    class Meta:
        verbose_name = "Classe d'Actif"
        verbose_name_plural = "Classes d'Actifs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Secteur(models.Model):
    """Secteurs économiques"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Secteur")
    
    class Meta:
        verbose_name = "Secteur"
        verbose_name_plural = "Secteurs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Pays(models.Model):
    """Pays d'investissement"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Pays")
    code = models.CharField(max_length=3, blank=True, verbose_name="Code pays")
    
    class Meta:
        verbose_name = "Pays"
        verbose_name_plural = "Pays"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class SecteurObligation(models.Model):
    """Secteurs spécifiques aux obligations"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Secteur obligation")
    
    class Meta:
        verbose_name = "Secteur Obligation"
        verbose_name_plural = "Secteurs Obligations"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Cotation(models.Model):
    """Types de cotation"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Type de cotation")
    
    class Meta:
        verbose_name = "Cotation"
        verbose_name_plural = "Cotations"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class CompositionFCP(models.Model):
    """Composition détaillée des FCP"""
    fcp = models.ForeignKey(FCP, on_delete=models.CASCADE, related_name='compositions')
    type_fcp = models.ForeignKey(
        TypeFCP, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Type de FCP"
    )
    classe = models.ForeignKey(
        ClasseActif, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Classe d'actif"
    )
    secteur = models.ForeignKey(
        Secteur, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Secteur"
    )
    pays = models.ForeignKey(
        Pays, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Pays"
    )
    secteur_obligation = models.ForeignKey(
        SecteurObligation, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Secteur obligation"
    )
    cotation = models.ForeignKey(
        Cotation, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Cotation"
    )
    pourcentage = models.DecimalField(
        max_digits=10, 
        decimal_places=6,
        validators=[MinValueValidator(0)],
        verbose_name="Pourcentage"
    )
    
    class Meta:
        verbose_name = "Composition FCP"
        verbose_name_plural = "Compositions FCP"
        ordering = ['fcp', '-pourcentage']
        indexes = [
            models.Index(fields=['fcp']),
        ]
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.pourcentage}%"


class Benchmark(models.Model):
    """Benchmarks de référence"""
    date = models.DateField(unique=True, verbose_name="Date")
    benchmark_obligataire = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Benchmark Obligataire"
    )
    benchmark_actions = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Benchmark Actions"
    )
    
    class Meta:
        verbose_name = "Benchmark"
        verbose_name_plural = "Benchmarks"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Benchmark - {self.date}"


class PoidsQuotidien(models.Model):
    """Poids quotidiens des différentes classes d'actifs pour chaque FCP"""
    fcp = models.ForeignKey(FCP, on_delete=models.CASCADE, related_name='poids_quotidiens')
    date = models.DateField(verbose_name="Date")
    actions = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Poids Actions (%)"
    )
    obligations = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Poids Obligations (%)"
    )
    opcvm = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Poids OPCVM (%)"
    )
    liquidites = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Poids Liquidités (%)"
    )
    
    class Meta:
        verbose_name = "Poids Quotidien"
        verbose_name_plural = "Poids Quotidiens"
        ordering = ['-date', 'fcp']
        unique_together = ['fcp', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['fcp', 'date']),
        ]
    
    def __str__(self):
        return f"{self.fcp.nom} - {self.date}"


class FicheSignaletique(models.Model):
    """Fiche signalétique des FCP avec informations générales"""
    fcp = models.OneToOneField(
        FCP, 
        on_delete=models.CASCADE, 
        related_name='fiche_signaletique',
        verbose_name="FCP"
    )
    echelle_risque = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Échelle de risque"
    )
    type_fcp = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Type de FCP"
    )
    horizon_investissement = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Horizon d'investissement (années)"
    )
    benchmark_obligataire = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Benchmark Obligataire"
    )
    benchmark_brvmc = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Benchmark BRVMC (Actions)"
    )
    date_creation = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de création"
    )
    depositaire = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Dépositaire"
    )
    frais_gestion = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        verbose_name="Frais de gestion (TTC de l'actif net / an)"
    )
    frais_entree = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        verbose_name="Frais d'entrée TTC"
    )
    frais_sortie = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        verbose_name="Frais de sortie TTC"
    )
    
    @property
    def profil_risque(self):
        """Détermine le profil de risque en fonction de l'échelle"""
        if self.echelle_risque is None:
            return "Non défini"
        elif self.echelle_risque <= 2:
            return "Prudent"
        elif self.echelle_risque <= 4:
            return "Équilibré"
        else:
            return "Dynamique"
    
    class Meta:
        verbose_name = "Fiche Signalétique"
        verbose_name_plural = "Fiches Signalétiques"
        ordering = ['fcp']
    
    def __str__(self):
        return f"Fiche - {self.fcp.nom}"
