# Migration corrective pour ajouter la colonne devise manquante
# Cette migration utilise RunSQL pour ajouter la colonne si elle n'existe pas

from django.db import migrations


def add_devise_if_missing(apps, schema_editor):
    """Ajoute la colonne devise si elle n'existe pas déjà"""
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Vérifier si la colonne existe
        cursor.execute("PRAGMA table_info(fcp_app_fichesignaletique);")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'devise' not in columns:
            cursor.execute(
                "ALTER TABLE fcp_app_fichesignaletique ADD COLUMN devise varchar(10) DEFAULT 'XOF';"
            )
            print("  ✓ Colonne 'devise' ajoutée à fcp_app_fichesignaletique")
        else:
            print("  → Colonne 'devise' existe déjà")


def reverse_migration(apps, schema_editor):
    """Reverse: ne fait rien car on ne veut pas supprimer la colonne"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fcp_app', '0006_fix_fichesignaletique_add_devise'),
    ]

    operations = [
        migrations.RunPython(add_devise_if_missing, reverse_migration),
    ]
