"""Tests pour l'application FCP - Gestion des Fonds Communs de Placement"""
from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
import json

from .models import (
    FicheSignaletique, 
    FCP_VL_MODELS, 
    get_vl_model,
    VL_FCP_Placement_Avantage,
    VL_FCP_Djolof,
    CompositionPoche,
    TypePoche,
    InstrumentAction,
    InstrumentObligation,
    BenchmarkObligation,
    BenchmarkBRVM,
)
from .data import FCP_FICHE_SIGNALETIQUE


class FicheSignaletiqueTests(TestCase):
    """Tests pour le modèle FicheSignaletique"""
    
    def setUp(self):
        """Créer un FCP de test"""
        self.fcp = FicheSignaletique.objects.create(
            nom="FCP TEST",
            echelle_risque=3,
            type_fond="Diversifié",
            horizon=5,
            benchmark_oblig=Decimal("60.00"),
            benchmark_brvmc=Decimal("40.00"),
            description="FCP de test",
            devise="XOF",
            gestionnaire="CGF Bourse"
        )
    
    def test_fcp_creation(self):
        """Test création d'une fiche signalétique"""
        self.assertEqual(self.fcp.nom, "FCP TEST")
        self.assertEqual(self.fcp.echelle_risque, 3)
        self.assertEqual(self.fcp.type_fond, "Diversifié")
    
    def test_fcp_str(self):
        """Test représentation string"""
        self.assertEqual(str(self.fcp), "FCP TEST")
    
    def test_risk_label_property(self):
        """Test propriété risk_label"""
        self.assertEqual(self.fcp.risk_label, "Modéré")
        
        # Tester différents niveaux
        self.fcp.echelle_risque = 1
        self.assertEqual(self.fcp.risk_label, "Très faible")
        
        self.fcp.echelle_risque = 7
        self.assertEqual(self.fcp.risk_label, "Maximum")
    
    def test_type_icon_property(self):
        """Test propriété type_icon pour Bootstrap"""
        self.assertEqual(self.fcp.type_icon, "bi bi-pie-chart-fill")
        
        self.fcp.type_fond = "Obligataire"
        self.assertEqual(self.fcp.type_icon, "bi bi-bank")
    
    def test_type_color_property(self):
        """Test propriété type_color"""
        self.assertEqual(self.fcp.type_color, "#004080")
    
    def test_unique_nom_constraint(self):
        """Test contrainte d'unicité sur le nom"""
        with self.assertRaises(Exception):
            FicheSignaletique.objects.create(
                nom="FCP TEST",  # Même nom
                echelle_risque=2,
                type_fond="Obligataire",
                horizon=3,
                benchmark_oblig=Decimal("100.00"),
                benchmark_brvmc=Decimal("0.00")
            )
    
    def test_benchmark_sum(self):
        """Test que les benchmarks peuvent sommer à 100%"""
        total = self.fcp.benchmark_oblig + self.fcp.benchmark_brvmc
        self.assertEqual(total, Decimal("100.00"))


class VLModelTests(TestCase):
    """Tests pour les modèles de Valeurs Liquidatives"""
    
    def setUp(self):
        """Créer FCP et VL de test"""
        self.fcp = FicheSignaletique.objects.create(
            nom="FCP PLACEMENT AVANTAGE",
            echelle_risque=3,
            type_fond="Diversifié",
            horizon=5,
            benchmark_oblig=Decimal("75.00"),
            benchmark_brvmc=Decimal("25.00")
        )
        
        # Créer des VL sur plusieurs jours
        self.today = date.today()
        self.vl_data = [
            (self.today - timedelta(days=30), Decimal("10000.0000")),
            (self.today - timedelta(days=20), Decimal("10050.0000")),
            (self.today - timedelta(days=10), Decimal("10100.0000")),
            (self.today, Decimal("10150.0000")),
        ]
        
        for date_vl, valeur in self.vl_data:
            VL_FCP_Placement_Avantage.objects.create(
                fcp=self.fcp,
                date=date_vl,
                valeur=valeur
            )
    
    def test_vl_creation(self):
        """Test création de valeurs liquidatives"""
        vl_count = VL_FCP_Placement_Avantage.objects.count()
        self.assertEqual(vl_count, 4)
    
    def test_vl_ordering(self):
        """Test que les VL sont ordonnées par date décroissante"""
        vls = list(VL_FCP_Placement_Avantage.objects.all())
        self.assertEqual(vls[0].date, self.today)  # Plus récent en premier
        self.assertEqual(vls[-1].date, self.today - timedelta(days=30))  # Plus ancien en dernier
    
    def test_vl_unique_date(self):
        """Test contrainte d'unicité sur la date"""
        with self.assertRaises(Exception):
            VL_FCP_Placement_Avantage.objects.create(
                fcp=self.fcp,
                date=self.today,  # Date déjà existante
                valeur=Decimal("10200.0000")
            )
    
    def test_get_vl_model_helper(self):
        """Test helper get_vl_model"""
        model = get_vl_model("FCP PLACEMENT AVANTAGE")
        self.assertEqual(model, VL_FCP_Placement_Avantage)
        
        # Test avec nom inexistant
        model_none = get_vl_model("FCP INEXISTANT")
        self.assertIsNone(model_none)
    
    def test_fcp_vl_models_mapping(self):
        """Test que tous les FCP ont un mapping VL"""
        self.assertEqual(len(FCP_VL_MODELS), 25)
        
        # Vérifier quelques mappings
        self.assertIn("FCP PLACEMENT AVANTAGE", FCP_VL_MODELS)
        self.assertIn("FCP DJOLOF", FCP_VL_MODELS)
        self.assertIn("FCPR SEN'FONDS", FCP_VL_MODELS)
    
    def test_vl_decimal_precision(self):
        """Test précision décimale des VL"""
        vl = VL_FCP_Placement_Avantage.objects.first()
        self.assertIsInstance(vl.valeur, Decimal)
        # 4 décimales
        self.assertEqual(vl.valeur.as_tuple().exponent, -4)


class CompositionTests(TestCase):
    """Tests pour les modèles de composition de portefeuille"""
    
    def setUp(self):
        """Créer FCP et composition de test"""
        self.fcp = FicheSignaletique.objects.create(
            nom="FCP TEST COMPO",
            echelle_risque=4,
            type_fond="Diversifié",
            horizon=5,
            benchmark_oblig=Decimal("50.00"),
            benchmark_brvmc=Decimal("50.00")
        )
        
        self.date_compo = date.today()
        
        # Créer poche Actions
        self.poche_action = CompositionPoche.objects.create(
            fcp=self.fcp,
            type_poche=TypePoche.ACTION,
            date_composition=self.date_compo,
            poids_poche=Decimal("40.00"),
            montant=Decimal("400000000.00")
        )
        
        # Créer poche Obligations
        self.poche_oblig = CompositionPoche.objects.create(
            fcp=self.fcp,
            type_poche=TypePoche.OBLIGATION,
            date_composition=self.date_compo,
            poids_poche=Decimal("50.00"),
            montant=Decimal("500000000.00")
        )
        
        # Créer poche Liquidité
        self.poche_liq = CompositionPoche.objects.create(
            fcp=self.fcp,
            type_poche=TypePoche.LIQUIDITE,
            date_composition=self.date_compo,
            poids_poche=Decimal("10.00"),
            montant=Decimal("100000000.00")
        )
    
    def test_poche_creation(self):
        """Test création des poches"""
        poches = CompositionPoche.objects.filter(fcp=self.fcp)
        self.assertEqual(poches.count(), 3)
    
    def test_poche_types(self):
        """Test types de poches disponibles"""
        self.assertEqual(TypePoche.ACTION, 'ACTION')
        self.assertEqual(TypePoche.OBLIGATION, 'OBLIGATION')
        self.assertEqual(TypePoche.LIQUIDITE, 'LIQUIDITE')
        self.assertEqual(TypePoche.FCP, 'FCP')
    
    def test_poche_unique_together(self):
        """Test contrainte unique_together (fcp, type_poche, date)"""
        with self.assertRaises(Exception):
            CompositionPoche.objects.create(
                fcp=self.fcp,
                type_poche=TypePoche.ACTION,  # Même type
                date_composition=self.date_compo,  # Même date
                poids_poche=Decimal("20.00")
            )
    
    def test_instrument_action(self):
        """Test création instrument action"""
        instrument = InstrumentAction.objects.create(
            poche=self.poche_action,
            nom="SONATEL",
            code_isin="SN0000000001",
            ticker="SNTS",
            secteur="Télécommunications",
            pays="Sénégal",
            quantite=Decimal("1000.0000"),
            prix_unitaire=Decimal("15000.0000"),
            valorisation=Decimal("15000000.00"),
            poids=Decimal("15.00")
        )
        
        self.assertEqual(instrument.nom, "SONATEL")
        self.assertEqual(instrument.ticker, "SNTS")
        self.assertEqual(str(instrument), "SONATEL - 15.00%")
    
    def test_instrument_obligation(self):
        """Test création instrument obligation"""
        instrument = InstrumentObligation.objects.create(
            poche=self.poche_oblig,
            nom="OAT SENEGAL 6% 2028",
            code_isin="SN0000000002",
            type_obligation="ETAT",
            emetteur="État du Sénégal",
            taux_nominal=Decimal("6.000"),
            date_echeance=date(2028, 12, 31),
            maturite_residuelle=Decimal("3.50"),
            valorisation=Decimal("100000000.00"),
            poids=Decimal("20.00")
        )
        
        self.assertEqual(instrument.type_obligation, "ETAT")
        self.assertEqual(instrument.emetteur, "État du Sénégal")


class BenchmarkTests(TestCase):
    """Tests pour les modèles de benchmarks"""
    
    def setUp(self):
        """Créer données benchmark de test"""
        self.today = date.today()
        
        BenchmarkObligation.objects.create(
            date=self.today,
            valeur=Decimal("105.5000"),
            variation_journaliere=Decimal("0.0500")
        )
        
        BenchmarkBRVM.objects.create(
            date=self.today,
            valeur=Decimal("250.7500"),
            variation_journaliere=Decimal("-0.2500")
        )
    
    def test_benchmark_oblig_creation(self):
        """Test création benchmark obligataire"""
        bench = BenchmarkObligation.objects.get(date=self.today)
        self.assertEqual(bench.valeur, Decimal("105.5000"))
    
    def test_benchmark_brvm_creation(self):
        """Test création benchmark BRVM"""
        bench = BenchmarkBRVM.objects.get(date=self.today)
        self.assertEqual(bench.valeur, Decimal("250.7500"))
        self.assertEqual(bench.variation_journaliere, Decimal("-0.2500"))


class APITests(TestCase):
    """Tests pour les endpoints API"""
    
    def setUp(self):
        """Créer données de test pour les APIs"""
        self.client = Client()
        
        # Créer FCP
        self.fcp = FicheSignaletique.objects.create(
            nom="FCP PLACEMENT AVANTAGE",
            echelle_risque=3,
            type_fond="Diversifié",
            horizon=5,
            benchmark_oblig=Decimal("75.00"),
            benchmark_brvmc=Decimal("25.00")
        )
        
        # Créer historique VL
        self.today = date.today()
        for i in range(365):
            d = self.today - timedelta(days=i)
            valeur = Decimal("10000") + Decimal(str(i * 0.5))
            VL_FCP_Placement_Avantage.objects.create(
                fcp=self.fcp,
                date=d,
                valeur=valeur
            )
    
    def test_valeurs_liquidatives_view(self):
        """Test page principale VL"""
        response = self.client.get(reverse('fcp_app:valeurs_liquidatives'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fcp_app/valeurs_liquidatives.html')
    
    def test_valeurs_liquidatives_with_fcp_param(self):
        """Test page VL avec paramètre FCP"""
        response = self.client.get(
            reverse('fcp_app:valeurs_liquidatives'),
            {'fcp': 'FCP PLACEMENT AVANTAGE'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FCP PLACEMENT AVANTAGE')
    
    def test_api_vl_data(self):
        """Test API données VL"""
        response = self.client.get(
            reverse('fcp_app:api_vl_data'),
            {'fcp': 'FCP PLACEMENT AVANTAGE'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        # L'API retourne {'data': [...]} avec la liste des VL
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    def test_api_vl_data_structure(self):
        """Test structure des données VL retournées"""
        response = self.client.get(
            reverse('fcp_app:api_vl_data'),
            {'fcp': 'FCP PLACEMENT AVANTAGE'}
        )
        data = json.loads(response.content)
        
        # Vérifier la structure de chaque entrée VL
        first_vl = data['data'][0]
        self.assertIn('date', first_vl)
        self.assertIn('valeur', first_vl)
        
        # Vérifier qu'on a bien 365 VL
        self.assertEqual(len(data['data']), 365)
    
    def test_composition_view(self):
        """Test page composition"""
        response = self.client.get(reverse('fcp_app:composition'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fcp_app/composition.html')
    
    def test_exportations_view(self):
        """Test page exportations"""
        response = self.client.get(reverse('fcp_app:exportations'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fcp_app/exportations.html')
    
    def test_a_propos_view(self):
        """Test page à propos"""
        response = self.client.get(reverse('fcp_app:a_propos'))
        self.assertEqual(response.status_code, 200)


class PerformanceCalculationTests(TestCase):
    """Tests pour les calculs de performance"""
    
    def setUp(self):
        """Créer données pour tester les calculs de performance"""
        self.client = Client()
        self.fcp = FicheSignaletique.objects.create(
            nom="FCP PLACEMENT AVANTAGE",
            echelle_risque=3,
            type_fond="Diversifié",
            horizon=5,
            benchmark_oblig=Decimal("75.00"),
            benchmark_brvmc=Decimal("25.00")
        )
        
        # VL de référence: 10000 il y a 1 an, 10500 aujourd'hui = +5%
        self.today = date.today()
        
        VL_FCP_Placement_Avantage.objects.create(
            fcp=self.fcp,
            date=self.today - timedelta(days=365),
            valeur=Decimal("10000.0000")
        )
        VL_FCP_Placement_Avantage.objects.create(
            fcp=self.fcp,
            date=self.today,
            valeur=Decimal("10500.0000")
        )
    
    def test_performance_calculation_manual(self):
        """Test calcul performance manuel"""
        # Performance = (10500 / 10000 - 1) * 100 = 5%
        vl_start = VL_FCP_Placement_Avantage.objects.filter(
            date=self.today - timedelta(days=365)
        ).first()
        vl_end = VL_FCP_Placement_Avantage.objects.filter(
            date=self.today
        ).first()
        
        perf = (float(vl_end.valeur) / float(vl_start.valeur) - 1) * 100
        self.assertAlmostEqual(perf, 5.0, places=1)
    
    def test_api_returns_vl_data(self):
        """Test que l'API retourne les données VL"""
        response = self.client.get(
            reverse('fcp_app:api_vl_data'),
            {'fcp': 'FCP PLACEMENT AVANTAGE'}
        )
        data = json.loads(response.content)
        
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 2)  # 2 VL créées


class DataIntegrityTests(TestCase):
    """Tests d'intégrité des données de référence"""
    
    def test_fcp_fiche_signaletique_data_exists(self):
        """Test que les données FCP_FICHE_SIGNALETIQUE existent"""
        self.assertGreater(len(FCP_FICHE_SIGNALETIQUE), 0)
        self.assertEqual(len(FCP_FICHE_SIGNALETIQUE), 25)
    
    def test_fcp_data_required_fields(self):
        """Test que chaque FCP a tous les champs requis"""
        required_fields = [
            'echelle_risque',
            'type_fond',
            'horizon',
            'benchmark_oblig',
            'benchmark_brvmc'
        ]
        
        for fcp_name, data in FCP_FICHE_SIGNALETIQUE.items():
            for field in required_fields:
                self.assertIn(
                    field, 
                    data, 
                    f"Champ {field} manquant pour {fcp_name}"
                )
    
    def test_fcp_vl_models_matches_fiche_data(self):
        """Test que FCP_VL_MODELS contient tous les FCP de FCP_FICHE_SIGNALETIQUE"""
        for fcp_name in FCP_FICHE_SIGNALETIQUE.keys():
            self.assertIn(
                fcp_name,
                FCP_VL_MODELS,
                f"FCP {fcp_name} n'a pas de modèle VL correspondant"
            )
    
    def test_risk_scale_valid_range(self):
        """Test que l'échelle de risque est entre 1 et 7"""
        for fcp_name, data in FCP_FICHE_SIGNALETIQUE.items():
            risk = data['echelle_risque']
            self.assertGreaterEqual(risk, 1, f"{fcp_name}: risque < 1")
            self.assertLessEqual(risk, 7, f"{fcp_name}: risque > 7")
    
    def test_benchmark_percentages_valid(self):
        """Test que les benchmarks sont des pourcentages valides"""
        for fcp_name, data in FCP_FICHE_SIGNALETIQUE.items():
            oblig = data['benchmark_oblig']
            brvmc = data['benchmark_brvmc']
            
            self.assertGreaterEqual(oblig, 0, f"{fcp_name}: benchmark_oblig < 0")
            self.assertLessEqual(oblig, 100, f"{fcp_name}: benchmark_oblig > 100")
            self.assertGreaterEqual(brvmc, 0, f"{fcp_name}: benchmark_brvmc < 0")
            self.assertLessEqual(brvmc, 100, f"{fcp_name}: benchmark_brvmc > 100")
            
            # La somme devrait être 100%
            self.assertEqual(
                oblig + brvmc, 
                100, 
                f"{fcp_name}: benchmarks ne somment pas à 100%"
            )
