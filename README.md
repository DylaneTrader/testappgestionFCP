# Gestion FCP

Application Django pour la gestion de Fonds Communs de Placement.

## Installation

1. Creer un environnement virtuel :
python -m venv venv

2. Activer l'environnement :
# Windows
venv\Scripts\activate

3. Installer les dependances :
pip install -r requirements.txt

4. Appliquer les migrations :
python manage.py migrate

5. Lancer le serveur de developpement :
python manage.py runserver

## Structure du projet

- gestionFCP/ - Configuration principale Django
- fcp_app/ - Application principale
