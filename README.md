# testappgestionFCP

Application Django de gestion de Fonds Communs de Placement (FCP).

## Fonctionnalités

L'application comprend les pages suivantes :
- **Page d'accueil** : Vue d'ensemble de l'application
- **Valeurs liquidatives** : Consultation des valeurs liquidatives des FCP
- **Composition FCP** : Détails de la composition des portefeuilles
- **Fiche signalétique** : Informations clés des FCP
- **Souscriptions rachats & Actifs net** : Gestion des souscriptions et rachats
- **À propos** : Informations sur l'application

## Schéma de couleurs

L'application utilise le schéma de couleurs suivant :
- **Couleur primaire** : `#004080` (Bleu foncé) - Titres, boutons principaux
- **Couleur secondaire** : `#333333` (Gris foncé) - Widgets, lignes, icônes
- **Couleur tertiaire** : `#E0DEDD` (Gris clair) - Fonds de cartes, hover

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/DylaneTrader/testappgestionFCP.git
cd testappgestionFCP
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Exécuter les migrations :
```bash
python manage.py migrate
```

4. Lancer le serveur de développement :
```bash
python manage.py runserver
```

5. Accéder à l'application dans votre navigateur :
```
http://127.0.0.1:8000/
```

## Structure du projet

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
