"""
test_determinisme.py — Test de déterminisme SPNX-16
====================================================
Vérifie que deux appels à chiffrer(M, K) donnent
toujours exactement le même résultat.
"""

import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cipher import chiffrer

tests_ok = 0
tests_ko = 0

def check(nom: str, condition: bool) -> None:
    global tests_ok, tests_ko
    if condition:
        print(f"  ✅ {nom}")
        tests_ok += 1
    else:
        print(f"  ❌ {nom}")
        tests_ko += 1

print("=" * 50)
print("   TESTS DÉTERMINISME — SPNX-16")
print("=" * 50)

print("\n[1] Cas fixes")
cas_fixes = [
    ("Hello", 0xABCD),
    ("A",     0x0001),
    ("Test",  0xFFFF),
]
for msg, cle in cas_fixes:
    c1 = chiffrer(msg, cle)
    c2 = chiffrer(msg, cle)
    check(f"'{msg}' avec clé 0x{cle:04X}", c1 == c2)

print("\n[2] 1000 appels aléatoires répétés")
random.seed(99)
erreurs = 0
for _ in range(1000):
    msg = ''.join(chr(random.randint(32, 126)) for _ in range(random.randint(1, 15)))
    cle = random.randint(0, 0xFFFF)
    if chiffrer(msg, cle) != chiffrer(msg, cle):
        erreurs += 1

check("1000 paires (M, K) : chiffrer() toujours identique", erreurs == 0)

print("\n[3] Même message, clés différentes → résultats différents")
msg = "SPNX16"
resultats = set()
for cle in [0x0000, 0x1111, 0xABCD, 0xFFFF, 0x8000]:
    resultats.add(chiffrer(msg, cle))
check("5 clés différentes → 5 résultats différents", len(resultats) == 5)

print("\n" + "=" * 50)
print(f"  Résultat : {tests_ok} OK  |  {tests_ko} ÉCHEC")
if tests_ko == 0:
    print("  🎉 Tous les tests de déterminisme sont passés !")
else:
    print("  ⚠️  Des tests ont échoué.")
print("=" * 50)