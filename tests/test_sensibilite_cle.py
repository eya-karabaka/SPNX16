"""
test_sensibilite_cle.py — Test de sensibilité à la clé SPNX-16
===============================================================
Vérifie que K ≠ K' implique chiffrer(M, K) ≠ chiffrer(M, K')
et qu'une mauvaise clé ne peut pas déchiffrer correctement.
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
print("  TESTS SENSIBILITÉ CLÉ — SPNX-16")
print("=" * 50)

print("\n[1] Clés différentes → chiffrés différents")
msg = "Hello SPNX"
cle = 0xABCD
for delta in [1, 2, 4, 8, 0x0100, 0x1000]:
    # Créer une nouvelle clé presque identique, mais avec certains bits modifiés :
    cle2 = cle ^ delta
    check(f"clé 0x{cle:04X} vs 0x{cle2:04X} (delta={delta})",
          chiffrer(msg, cle) != chiffrer(msg, cle2))

# Remarque : On a choisi des puissances de deux comme valeurs de la liste parce qu'en binaire, elles permettent 
# de modifier un seul bit à la fois (ou des positions précises de bits)
# pour tester la sensibilité de la clé aux petites modifications.

print("\n[2] Mauvaise clé ne déchiffre pas correctement (1000 cas)")
# Interet : Si quelqu'un possède un texte chiffré mais utilise une mauvaise clé, 
# est-ce qu'il peut quand même retrouver le message original ?
random.seed(77) # Fixe la séquence aléatoire
erreurs = 0
for _ in range(1000):
    msg = ''.join(chr(random.randint(32, 126)) for _ in range(random.randint(1, 10)))
    cle = random.randint(0, 0xFFFF)
    cle_fausse = cle ^ random.randint(1, 0xFFFF)  # clé forcément différente
    chiffre = chiffrer(msg, cle)
    try:
        resultat = dechiffrer(chiffre, cle_fausse)
        if resultat == msg:
            erreurs += 1   # collision (rarissime mais possible)
    except Exception:
        pass  # padding invalide = clé incorrecte détectée ✅

# une mauvaise clé peut provoquer une erreur car parce que,
# les données sont complétées avec du padding
# donc l'erreur signifie :La mauvaise clé n'a même pas réussi à produire un texte déchiffrable valide.
# Le programme regarde la fin: Il s'attend à trouver un padding correct
# Mais il trouve d'autres caractères 
# Ainsi cette clé n'a pas réussi à produire un message valide

check("1000 cas : mauvaise clé ne retrouve pas le message", erreurs == 0)

print("\n[3] Modifier 1 bit de la clé change le chiffré")
msg = "Test"
cle = 0b1010101111001101
for bit in range(16):
    cle_modifiee = cle ^ (1 << bit)
    ok = chiffrer(msg, cle) != chiffrer(msg, cle_modifiee)
    check(f"Bit {bit:2d} modifié → chiffré différent", ok)

print("\n" + "=" * 50)
print(f"  Résultat : {tests_ok} OK  |  {tests_ko} ÉCHEC")
if tests_ko == 0:
    print("  🎉 Tous les tests de sensibilité clé sont passés !")
else:
    print("  ⚠️  Des tests ont échoué.")
print("=" * 50)