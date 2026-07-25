"""
bruteforce.py — Attaque par Force Brute SPNX-16
================================================
Teste exhaustivement les 2^16 = 65 536 clés possibles
pour retrouver la clé secrète à partir d'un couple
(message_clair, message_chiffré) connu.

Démontre concrètement la faiblesse d'une clé de 16 bits
et permet d'extrapoler le temps nécessaire pour casser
des espaces de clés plus grands (32, 64, 128 bits).
"""

import sys, os, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.cipher import chiffrer, dechiffrer


# ─── Attaque principale ───────────────────────────────────────────────────────

def attaque_force_brute(message_clair: str,
                         message_chiffre: bytes) -> dict:
    """
    Teste toutes les clés de 0x0000 à 0xFFFF pour retrouver
    celle qui produit le chiffré connu à partir du clair connu.

    Args:
        message_clair   : str   — le message en clair connu
        message_chiffre : bytes — le message chiffré correspondant

    Returns:
        dict avec les clés :
            - 'cle_trouvee'   : int  — la clé retrouvée (ou None)
            - 'temps_secondes': float — temps d'exécution
            - 'cles_testees'  : int  — nombre de clés testées
            - 'debit'         : float — clés par seconde
            - 'succes'        : bool
    """
    print("=" * 55)
    print("     ATTAQUE FORCE BRUTE — SPNX-16")
    print("=" * 55)
    print(f"\n  Message clair   : {repr(message_clair)}")
    print(f"  Message chiffré : {message_chiffre.hex()}")
    print(f"  Espace de clés  : 2^16 = 65 536 clés")
    print("\n  Attaque en cours...\n")

    cle_trouvee  = None
    cles_testees = 0
    debut        = time.perf_counter()

    for cle in range(0x10000):  # 0 à 65535
        cles_testees += 1

        # Afficher la progression toutes les 10 000 clés
        if cles_testees % 10000 == 0:
            progression = (cles_testees / 65536) * 100
            print(f"  Progression : {progression:.0f}%  "
                  f"({cles_testees}/65536 clés testées)...")

        # Tester si cette clé reproduit le chiffré connu
        try:
            essai = chiffrer(message_clair, cle)
            if essai == message_chiffre:
                cle_trouvee = cle
                break
        except Exception:
            continue

    fin            = time.perf_counter()
    temps          = fin - debut
    debit          = cles_testees / temps if temps > 0 else 0

    return {
        'cle_trouvee'    : cle_trouvee,
        'temps_secondes' : temps,
        'cles_testees'   : cles_testees,
        'debit'          : debit,
        'succes'         : cle_trouvee is not None,
    }


# ─── Attaque par dictionnaire (bonus) ────────────────────────────────────────

def attaque_dictionnaire(message_clair: str,
                          message_chiffre: bytes) -> dict:
    """
    Teste d'abord un sous-ensemble de clés "courantes" avant
    de lancer la force brute complète.

    Illustre pourquoi utiliser une clé simple est dangereux :
    ces clés courantes sont testées en priorité.

    Args:
        message_clair   : str
        message_chiffre : bytes

    Returns:
        dict — résultat (même structure que attaque_force_brute)
    """
    cles_courantes = [
        0x0000, 0xFFFF, 0xAAAA, 0x5555,
        0x1234, 0xABCD, 0x0001, 0x8000,
        0x1111, 0x2222, 0x3333, 0x4444,
        0xDEAD, 0xBEEF, 0xCAFE, 0xFACE,
    ]

    print("=" * 55)
    print("  ATTAQUE DICTIONNAIRE — SPNX-16")
    print("=" * 55)
    print(f"\n  Test de {len(cles_courantes)} clés courantes en priorité...")

    debut = time.perf_counter()

    for cle in cles_courantes:
        try:
            if chiffrer(message_clair, cle) == message_chiffre:
                temps = time.perf_counter() - debut
                print(f"  ✅ Clé trouvée dans le dictionnaire : 0x{cle:04X}")
                return {
                    'cle_trouvee'    : cle,
                    'temps_secondes' : temps,
                    'cles_testees'   : cles_courantes.index(cle) + 1,
                    'debit'          : (cles_courantes.index(cle) + 1) / temps,
                    'succes'         : True,
                    'methode'        : 'dictionnaire',
                }
        except Exception:
            continue

    print("  Clé non trouvée dans le dictionnaire.")
    print("  Passage à la force brute complète...\n")

    resultat = attaque_force_brute(message_clair, message_chiffre)
    resultat['methode'] = 'force_brute'
    return resultat


# ─── Extrapolation théorique ──────────────────────────────────────────────────

def extrapoler(debit: float) -> None:
    """
    À partir du débit mesuré (clés/seconde), calcule le temps
    théorique pour casser des espaces de clés plus grands.

    Args:
        debit : float — clés testées par seconde
    """
    print("\n" + "=" * 55)
    print("  EXTRAPOLATION THÉORIQUE")
    print("=" * 55)
    print(f"\n  Débit mesuré : {debit:,.0f} clés/seconde\n")

    espaces = [
        (16,  "SPNX-16 (ce projet)"),
        (32,  "DES simplifié       "),
        (56,  "DES original        "),
        (64,  "Blowfish min        "),
        (128, "AES-128             "),
        (192, "AES-192             "),
        (256, "AES-256             "),
    ]

    unites = [
        (1,                    "secondes"),
        (60,                   "minutes"),
        (3600,                 "heures"),
        (86400,                "jours"),
        (86400 * 365,          "années"),
        (86400 * 365 * 1000,   "millénaires"),
    ]

    for bits, nom in espaces:
        nb_cles      = 2 ** bits
        temps_sec    = nb_cles / debit

        # Trouver l'unité la plus lisible
        temps_affiche = temps_sec
        unite_affiche = "secondes"
        for diviseur, unite in unites:
            if temps_sec >= diviseur:
                temps_affiche = temps_sec / diviseur
                unite_affiche = unite

        print(f"  {bits:3d} bits ({nom}) : "
              f"2^{bits:3d} clés → "
              f"{temps_affiche:,.2f} {unite_affiche}")

    print("\n  ℹ️  En réalité, AES-128 est considéré incassable")
    print("      par force brute avec la technologie actuelle.")
    print("=" * 55)


# ─── Affichage du résultat ────────────────────────────────────────────────────

def afficher_resultat(resultat: dict) -> None:
    """
    Affiche le résultat de l'attaque de façon lisible.

    Args:
        resultat : dict retourné par attaque_force_brute()
    """
    print("\n" + "=" * 55)
    print("  RÉSULTAT DE L'ATTAQUE")
    print("=" * 55)

    if resultat['succes']:
        cle = resultat['cle_trouvee']
        print(f"\n  ✅ CLÉ TROUVÉE !")
        print(f"     Clé (décimal) : {cle}")
        print(f"     Clé (hex)     : 0x{cle:04X}")
        print(f"     Clé (binaire) : {cle:016b}")
    else:
        print("\n  ❌ Clé non trouvée (espace épuisé)")

    print(f"\n  Clés testées    : {resultat['cles_testees']:,}")
    print(f"  Temps écoulé    : {resultat['temps_secondes']:.4f} secondes")
    print(f"  Débit           : {resultat['debit']:,.0f} clés/seconde")
    print("=" * 55)

    # Extrapolation
    extrapoler(resultat['debit'])


# ─── Test rapide si lancé directement ────────────────────────────────────────

if __name__ == "__main__":
    # Simuler une situation réelle : on connaît le clair et le chiffré
    # mais pas la clé
    cle_secrete     = 0x1A2B   # clé que l'attaquant ne connaît pas
    message_clair   = "X"      # message connu (known plaintext attack)
    message_chiffre = chiffrer(message_clair, cle_secrete)

    print(f"  [Simulation] Clé secrète réelle : 0x{cle_secrete:04X}")
    print(f"  [Simulation] L'attaquant connaît le clair et le chiffré")
    print(f"  [Simulation] Objectif : retrouver 0x{cle_secrete:04X}\n")

    # Lancer l'attaque
    resultat = attaque_force_brute(message_clair, message_chiffre)
    afficher_resultat(resultat)

    # Vérification
    if resultat['succes']:
        cle_retrouvee = resultat['cle_trouvee']
        verification  = chiffrer(message_clair, cle_retrouvee) == message_chiffre
        print(f"\n  Vérification finale : {'✅ OK' if verification else '❌ ERREUR'}")
        print(f"  Clé attendue  : 0x{cle_secrete:04X}")
        print(f"  Clé retrouvée : 0x{cle_retrouvee:04X}")
        print(f"  Identiques    : {'✅ OUI' if cle_secrete == cle_retrouvee else '❌ NON'}")