# Structure de la Base de Données SQL - Gestion FCP

## Vue d'ensemble

Le fichier Excel `data_fcp.xlsx` a été migré avec succès vers une base de données SQLite Django. La base de données comprend **14 modèles** interconnectés qui préservent toutes les relations entre les différentes feuilles Excel.

## Statistiques de Migration

- **FCPs**: 25 fonds
- **Valeurs Liquidatives**: 17 109 enregistrements
- **Souscriptions/Rachats**: 3 306 opérations
- **Actifs Nets**: 14 551 enregistrements
- **Compositions**: 2 331 lignes
- **Benchmarks**: 753 enregistrements
- **Poids Quotidiens**: 16 566 enregistrements

---

## Structure des Modèles

### 1. **FCP** (Table principale)
Représente les Fonds Communs de Placement.

**Champs**:
- `nom`: Nom du FCP (unique)
- `date_creation`: Date de création
- `actif`: Statut actif/inactif

**Relations**:
- Lié à tous les autres modèles via des clés étrangères

---

### 2. **ValeurLiquidative**
Stocke les valeurs liquidatives quotidiennes pour chaque FCP.

**Source Excel**: Feuille `Valeurs Liquidatives`

**Champs**:
- `fcp`: Clé étrangère vers FCP
- `date`: Date de la valeur
- `valeur`: Valeur liquidative (Decimal)

**Index**: 
- Index sur `date`
- Index composite sur `(fcp, date)`

**Contrainte**: Unicité sur `(fcp, date)`

---

### 3. **SouscriptionRachat**
Enregistre les opérations de souscriptions et rachats.

**Source Excel**: Feuille `Souscriptions Rachats`

**Champs**:
- `date`: Date de l'opération
- `type_client`: Clé étrangère vers TypeClient
- `type_operation`: Clé étrangère vers TypeOperation
- `fcp`: Clé étrangère vers FCP
- `montant`: Montant de l'opération

**Types de clients**:
- 1.Clients particuliers
- 2.Personnes Morales
- 3.OPCVM
- 4.Plans d'Epargne et FCPE

**Types d'opérations**:
- Souscriptions
- Rachats

---

### 4. **ActifNet**
Stocke les actifs nets quotidiens pour chaque FCP.

**Source Excel**: Feuille `Actifs Nets`

**Champs**:
- `fcp`: Clé étrangère vers FCP
- `date`: Date
- `montant`: Montant de l'actif net

**Contrainte**: Unicité sur `(fcp, date)`

---

### 5. **CompositionFCP**
Détaille la composition des portefeuilles de chaque FCP.

**Source Excel**: Feuille `Composition FCP`

**Champs**:
- `fcp`: Clé étrangère vers FCP
- `type_fcp`: Clé étrangère vers TypeFCP (Actions, Obligataires, Diversifiés)
- `classe`: Clé étrangère vers ClasseActif (Actions, Obligations, OPCVM, Liquidités)
- `secteur`: Clé étrangère vers Secteur
- `pays`: Clé étrangère vers Pays
- `secteur_obligation`: Clé étrangère vers SecteurObligation
- `cotation`: Clé étrangère vers Cotation
- `pourcentage`: Pourcentage de la composition

**Secteurs disponibles**:
- Agriculture
- Distribution
- Finance
- Industrie
- Services publics
- Transport
- Autres secteurs

**Pays disponibles**:
- Bénin, Burkina Faso, Côte d'Ivoire, Guinée-Bissau, Mali, Niger, Sénégal, Togo

---

### 6. **Benchmark**
Stocke les benchmarks de référence.

**Source Excel**: Feuille `Benchmarks`

**Champs**:
- `date`: Date (unique)
- `benchmark_obligataire`: Valeur du benchmark obligataire
- `benchmark_actions`: Valeur du benchmark actions

---

### 7. **PoidsQuotidien**
Stocke les poids quotidiens des différentes classes d'actifs.

**Source Excel**: Feuille `Poids Quotidiens`

**Champs**:
- `fcp`: Clé étrangère vers FCP
- `date`: Date
- `actions`: Poids des actions (%)
- `obligations`: Poids des obligations (%)
- `opcvm`: Poids des OPCVM (%)
- `liquidites`: Poids des liquidités (%)

**Contrainte**: Unicité sur `(fcp, date)`

---

### 8-14. **Tables de Référence**

Ces tables stockent les valeurs uniques référencées dans d'autres modèles:

- **TypeClient**: Types de clients
- **TypeOperation**: Types d'opérations (Souscriptions/Rachats)
- **TypeFCP**: Types de FCP (Actions, Obligataires, Diversifiés)
- **ClasseActif**: Classes d'actifs
- **Secteur**: Secteurs économiques
- **Pays**: Pays d'investissement
- **SecteurObligation**: Secteurs spécifiques aux obligations (Etat, Institutionnel, Regional)
- **Cotation**: Types de cotation (Coté, Non coté)

---

## Relations entre les Tables

```
FCP (Hub central)
├── ValeurLiquidative (1-N)
├── SouscriptionRachat (1-N)
├── ActifNet (1-N)
├── CompositionFCP (1-N)
└── PoidsQuotidien (1-N)

SouscriptionRachat
├── TypeClient (N-1)
└── TypeOperation (N-1)

CompositionFCP
├── TypeFCP (N-1)
├── ClasseActif (N-1)
├── Secteur (N-1)
├── Pays (N-1)
├── SecteurObligation (N-1)
└── Cotation (N-1)

Benchmark (Table indépendante)
```

---

## Avantages de la Base SQL

### 1. **Performance**
- Index optimisés sur les dates et les FCP
- Requêtes beaucoup plus rapides qu'Excel
- Bulk insert/update efficaces

### 2. **Intégrité des Données**
- Contraintes d'unicité sur les combinaisons (fcp, date)
- Clés étrangères garantissent la cohérence référentielle
- Validation des types de données

### 3. **Scalabilité**
- Peut gérer des millions d'enregistrements
- Requêtes optimisées avec des index
- Gestion efficace de la mémoire

### 4. **Maintenance**
- Facile d'ajouter de nouvelles données
- Mise à jour sélective possible
- Historique complet préservé

### 5. **Requêtes Complexes**
- Agrégations sur plusieurs tables
- Jointures efficaces
- Filtrage multi-critères

---

## Utilisation

### Accès via l'Admin Django
```bash
python manage.py createsuperuser
python manage.py runserver
```
Accédez à `http://localhost:8000/admin/`

### Utilisation dans les Views
```python
from fcp_app.models import FCP, ValeurLiquidative

# Obtenir toutes les valeurs liquidatives d'un FCP
fcp = FCP.objects.get(nom="FCP ACTIONS PHARMACIE")
valeurs = fcp.valeurs_liquidatives.all().order_by('-date')

# Obtenir les valeurs d'une période
from datetime import date
valeurs_2024 = ValeurLiquidative.objects.filter(
    date__year=2024,
    fcp=fcp
)

# Agrégations
from django.db.models import Sum, Avg
stats = SouscriptionRachat.objects.filter(
    fcp=fcp,
    type_operation__nom="Souscriptions"
).aggregate(
    total=Sum('montant'),
    moyenne=Avg('montant')
)
```

### Mise à Jour des Données
Pour ajouter de nouvelles données depuis Excel:
```bash
python migrate_excel_to_db.py
```

---

## Script de Migration

Le script `migrate_excel_to_db.py` effectue:
1. Lecture de toutes les feuilles Excel
2. Création des entités de référence
3. Migration des données avec gestion des erreurs
4. Insertion en bulk pour performance optimale
5. Gestion des duplications (ignore_conflicts)

**Durée de migration**: ~13 secondes pour 54 616 enregistrements

---

## Fichiers Modifiés/Créés

- ✅ `fcp_app/models.py` - Modèles Django
- ✅ `fcp_app/admin.py` - Configuration Admin
- ✅ `fcp_app/migrations/0001_initial.py` - Migration initiale
- ✅ `migrate_excel_to_db.py` - Script de migration
- ✅ `db.sqlite3` - Base de données (mise à jour)

---

## Prochaines Étapes Recommandées

1. **Créer des vues Django** pour afficher les données
2. **Ajouter des API REST** (Django REST Framework)
3. **Créer des graphiques** avec Chart.js ou Plotly
4. **Ajouter un système d'import** pour mettre à jour régulièrement
5. **Optimiser les requêtes** avec select_related/prefetch_related
6. **Ajouter des calculs** (rendements, performances, etc.)

---

## Notes Importantes

- ⚠️ Le fichier Excel `data_fcp.xlsx` peut être conservé comme backup mais n'est plus nécessaire pour l'application
- ✅ Toutes les données sont maintenant dans `db.sqlite3`
- ✅ Les relations entre les feuilles ont été préservées via les clés étrangères
- ✅ L'intégrité des données est garantie par les contraintes de la base de données
