"""Script de test des corrections de l'étape 1"""
import os
import sqlite3

# Test direct SQLite
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== TEST CORRECTIONS ETAPE 1 ===")
print()

# Test 1: Vérifier colonne devise
cursor.execute("PRAGMA table_info(fcp_app_fichesignaletique);")
columns = [row[1] for row in cursor.fetchall()]
print("1. Colonne 'devise' presente:", 'devise' in columns)

# Test 2: Vérifier les types de fond
cursor.execute("SELECT DISTINCT type_fond FROM fcp_app_fichesignaletique;")
types = [row[0] for row in cursor.fetchall()]
print("2. Types de fond en base:", types)
print("   Capital-Risque present:", 'Capital-Risque' in types)

# Test 3: Vérifier FCPR SEN'FONDS
cursor.execute("SELECT nom, type_fond, devise FROM fcp_app_fichesignaletique WHERE nom = ?", ("FCPR SEN'FONDS",))
row = cursor.fetchone()
if row:
    print(f"3. FCPR SEN'FONDS: type={row[1]}, devise={row[2]}")
else:
    print("3. FCPR SEN'FONDS non trouvé!")

# Test 4: Compter les FCP
cursor.execute("SELECT COUNT(*) FROM fcp_app_fichesignaletique;")
count = cursor.fetchone()[0]
print(f"4. Total FCP en base: {count}")

conn.close()
print()
print("=== FIN DES TESTS ===")
