"""
test_lat.py — Tests unitaires de la LAT SPNX-16
================================================
Vérifie les propriétés mathématiques garanties de la LAT
et la qualité de non-linéarité de la S-Box.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.lat import calculer_lat, valeur_max_lat, parite

tests_ok = 0
tests_ko = 0

def check(nom: str, condition: bool) -> None:
    global tests_ok, tests_ko
    if condition:
        print(f" ✅ {nom}")
        tests_ok += 1
    else:
        print(f" ❌ {nom}")
        tests_ko += 1

print("=" * 50)
print(" TESTS LAT — SPNX-16")
print("=" * 50)

lat = calculer_lat()

print("\n[1] Propriétés structurelles")
check("LAT est une matrice 16x16", len(lat) == 16 and all(len(row) == 16 for row in lat))
check("LAT[0][0] == 8 (biais trivial garanti)", lat[0][0] == 8)
check("Tous les biais dans [-8, 8]",
      all(-8 <= lat[a][b] <= 8 for a in range(16) for b in range(16)))

print("\n[2] Fonction parité")
check("parite(0) == 0", parite(0) == 0)
check("parite(1) == 1", parite(1) == 1)
check("parite(3) == 0 (0011 -> deux bits à 1)", parite(3) == 0)
check("parite(7) == 1 (0111 -> trois bits à 1)", parite(7) == 1)

print("\n[3] Qualité de la non-linéarité")
valmax = valeur_max_lat(lat)
print(f"    Biais max observé (hors [0][0]) : {valmax}")
check("Biais max <= 6 (résistance linéaire acceptable)", valmax <= 6)

print("\n" + "=" * 50)
print(f" Résultat : {tests_ok} OK | {tests_ko} ÉCHEC")
if tests_ko == 0:
    print(" 🎉 Tous les tests LAT sont passés !")
else:
    print(" ⚠️ Des tests ont échoué.")
print("=" * 50)