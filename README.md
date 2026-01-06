# Application de Gestion de Fonds Communs de Placement (FCP)

Application Django moderne et performante pour la gestion et l'analyse de Fonds Communs de Placement, avec migration des données Excel vers une base SQL optimisée.

## 🎯 Fonctionnalités

### Pages de l'application
- **Page d'accueil** : Vue d'ensemble et statistiques globales
- **Valeurs liquidatives** : Consultation et suivi des valeurs liquidatives des FCP
- **Composition FCP** : Analyse détaillée de la composition des portefeuilles
- **Fiche signalétique** : Informations clés et statistiques par FCP
- **Souscriptions rachats & Actifs nets** : Gestion et suivi des opérations
- **À propos** : Informations sur l'application et statistiques globales

### Base de données SQL
✅ **Migration Excel → SQL terminée avec succès !**

L'application utilise maintenant une base de données SQL performante contenant :
- **25 FCPs** avec leurs données complètes
- **17 109** valeurs liquidatives
- **3 306** opérations (souscriptions/rachats)
- **14 551** actifs nets
- **2 331** compositions de portefeuilles
- **753** benchmarks
- **16 566** poids quotidiens

### Avantages de la base SQL
- ⚡ **Performance** : Requêtes 10x plus rapides qu'Excel
- 🔒 **Intégrité** : Contraintes et validations automatiques
- 📈 **Scalabilité** : Gère des millions d'enregistrements
- 🔄 **Concurrence** : Accès simultané multi-utilisateurs
- 🔍 **Requêtes complexes** : Agrégations et jointures optimisées

## 🚀 Installation

1. **Cloner le dépôt**
```bash
git clone https://github.com/DylaneTrader/testappgestionFCP.git
cd testappgestionFCP
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Les données sont déjà migrées !**
La base de données SQLite (`db.sqlite3`) contient déjà toutes les données.

4. **Créer un superutilisateur (optionnel)**
```bash
python manage.py createsuperuser
```

5. **Lancer le serveur**
```bash
python manage.py runserver
```

6. **Accéder à l'application**
- Application : http://127.0.0.1:8000/
- Administration : http://127.0.0.1:8000/admin/

## 📊 Structure de la Base de Données

### Modèles principaux

#### FCP (Hub central)
- Représente chaque Fonds Commun de Placement
- Lié à toutes les autres tables

#### ValeurLiquidative
- Valeurs liquidatives quotidiennes par FCP
- Index optimisés sur date et FCP

#### SouscriptionRachat
- Enregistrement des opérations
- Relations : TypeClient, TypeOperation, FCP

#### ActifNet
- Actifs nets quotidiens par FCP
- Suivi de l'évolution du patrimoine

#### CompositionFCP
- Détails de la composition des portefeuilles
- Relations : TypeFCP, ClasseActif, Secteur, Pays

#### Benchmark
- Benchmarks de référence (Obligataire, Actions)

#### PoidsQuotidien
- Répartition quotidienne par classe d'actif
- Actions, Obligations, OPCVM, Liquidités

### Relations
```
FCP (Hub central)
├── ValeurLiquidative (1-N)
├── SouscriptionRachat (1-N)
├── ActifNet (1-N)
├── CompositionFCP (1-N)
└── PoidsQuotidien (1-N)
```

## 🛠️ Scripts Utiles

### Mettre à jour les données depuis Excel
```bash
python update_from_excel.py
```

### Benchmark de performance Excel vs SQL
```bash
python benchmark_performance.py
```

### Exemples de requêtes
Voir le fichier `exemples_requetes.py` pour des exemples d'utilisation de l'ORM Django.

## 📁 Structure du Projet

```
testappgestionFCP/
├── gestionFCP/          # Configuration du projet Django
│   ├── settings.py      # Paramètres du projet
│   ├── urls.py          # URLs principales
│   └── ...
├── fcp_app/             # Application Django
│   ├── templates/       # Templates HTML
│   ├── static/          # Fichiers statiques (CSS)
│   ├── views.py         # Vues de l'application
│   ├── urls.py          # URLs de l'application
│   └── ...
├── manage.py            # Script de gestion Django
└── requirements.txt     # Dépendances Python
```

## Développement

Pour créer un superutilisateur (administrateur) :
```bash
python manage.py createsuperuser
```

Pour accéder à l'interface d'administration :
```
http://127.0.0.1:8000/admin/
```
