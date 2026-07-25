"""
test_reversibilite.py — Test de réversibilité SPNX-16
======================================================
Vérifie que dechiffrer(chiffrer(M, K), K) == M
pour un grand nombre de messages et clés aléatoires.
"""

import sys, os, random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cipher import chiffrer, dechiffrer

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
print("   TESTS RÉVERSIBILITÉ — SPNX-16")
print("=" * 50)

print("\n[1] Cas fixes")
cas_fixes = [
    ("A",             0xABCD),
    ("Hello",         0x1234),
    ("SPNX-16 !",     0xFFFF),
    ("",              0x0001),
    ("a",             0x0000),
    ("Test padding",  0x8000),
]
for msg, cle in cas_fixes:
    resultat = dechiffrer(chiffrer(msg, cle), cle)
    check(f"'{msg}' avec clé 0x{cle:04X}", resultat == msg)

print("\n[2] Messages aléatoires (1000 cas)")
random.seed(42)
erreurs = []
for _ in range(1000):
    longueur = random.randint(1, 20)
    msg = ''.join(chr(random.randint(32, 126)) for _ in range(longueur))
    cle = random.randint(0, 0xFFFF)
    try:
        resultat = dechiffrer(chiffrer(msg, cle), cle)
        if resultat != msg:
            erreurs.append((msg, cle))
    except Exception as e:
        erreurs.append((msg, cle))

check("1000 messages aléatoires réversibles", len(erreurs) == 0)
if erreurs:
    print(f"     Premiers échecs : {erreurs[:3]}")

print("\n[3] Cas limites")
check("Message d'un seul caractère",
      dechiffrer(chiffrer("X", 0x1111), 0x1111) == "X")
check("Message avec espaces",
      dechiffrer(chiffrer("   ", 0x2222), 0x2222) == "   ")
check("Message avec chiffres",
      dechiffrer(chiffrer("12345", 0x3333), 0x3333) == "12345")
check("Clé minimale (0x0000)",
      dechiffrer(chiffrer("test", 0x0000), 0x0000) == "test")
check("Clé maximale (0xFFFF)",
      dechiffrer(chiffrer("test", 0xFFFF), 0xFFFF) == "test")

print("\n" + "=" * 50)
print(f"  Résultat : {tests_ok} OK  |  {tests_ko} ÉCHEC")
if tests_ko == 0:
    print("  🎉 Tous les tests de réversibilité sont passés !")
else:
    print("  ⚠️  Des tests ont échoué.")
print("=" * 50)