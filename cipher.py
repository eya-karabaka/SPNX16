"""
cipher.py — Moteur de Chiffrement/Déchiffrement SPNX-16
========================================================
Assemble tous les modules pour exécuter les 4 rounds de SPNX-16.

Chiffrement (bloc par bloc) :
    Round 1 : XOR(K1) → Substitution → Permutation
    Round 2 : XOR(K2) → Substitution → Permutation
    Round 3 : XOR(K3) → Substitution → Permutation
    Round 4 : XOR(K4) → Substitution → XOR(K5)  ← pas de permutation

Déchiffrement : exactement l'inverse, dans l'ordre inverse des rounds.
"""

from sbox        import substituer_bloc
from permutation import permuter
from key_schedule import key_schedule
from padding     import (ajouter_padding, retirer_padding,
                               message_vers_octets, octets_vers_message)


# ─── Chiffrement d'un seul bloc de 8 bits ────────────────────────────────────

def chiffrer_bloc(bloc: int, sous_cles: list) -> int:
    """
    Chiffre un seul bloc de 8 bits à travers les 4 rounds de SPNX-16.
    - Args: bloc : entier 0-255 (8 bits) = le bloc à chiffrer
            sous_cles : liste [K1, K2, K3, K4, K5] générée par key_schedule()
    - Returns:
            entier 0-255 — le bloc chiffré
    """
    K1, K2, K3, K4, K5 = sous_cles

    # ── Round 1 ──────────────────────────────────────────────────
    bloc = bloc ^ K1              # Étape 1 : XOR avec K1
    bloc = substituer_bloc(bloc)  # Étape 2 : Substitution (2× S-Box)
    bloc = permuter(bloc)         # Étape 3 : Permutation

    # ── Round 2 ──────────────────────────────────────────────────
    bloc = bloc ^ K2
    bloc = substituer_bloc(bloc)
    bloc = permuter(bloc)

    # ── Round 3 ──────────────────────────────────────────────────
    bloc = bloc ^ K3
    bloc = substituer_bloc(bloc)
    bloc = permuter(bloc)

    # ── Round 4 (final) — pas de permutation ─────────────────────
    bloc = bloc ^ K4              # Étape 1 : XOR avec K4
    bloc = substituer_bloc(bloc)  # Étape 2 : Substitution
    bloc = bloc ^ K5              # Étape 3 : Whitening final avec K5

    return bloc


# ─── Déchiffrement d'un seul bloc de 8 bits ──────────────────────────────────

def dechiffrer_bloc(bloc: int, sous_cles: list) -> int:
    """
    - Déchiffre un seul bloc de 8 bits — inverse exact de chiffrer_bloc().
    - Ordre inverse des rounds, opérations inversées :
        - XOR est sa propre inverse  (A ^ K ^ K = A)
        - Substitution inverse       (INV_SBOX)
        - Permutation inverse        (INV_PERM)
    - Args:
        - bloc      : entier 0-255 (8 bits) — le bloc chiffré
        - sous_cles : liste [K1, K2, K3, K4, K5]
    - Returns:
        entier 0-255 — le bloc déchiffré
    """
    K1, K2, K3, K4, K5 = sous_cles

    # ── Round 4 inverse ───────────────────────────────────────────
    bloc = bloc ^ K5                          # Inverse du whitening K5
    bloc = substituer_bloc(bloc, inverse=True) # INV_SBOX
    bloc = bloc ^ K4                          # Inverse du XOR K4

    # ── Round 3 inverse ───────────────────────────────────────────
    bloc = permuter(bloc, inverse=True)        # INV_PERM
    bloc = substituer_bloc(bloc, inverse=True) # INV_SBOX
    bloc = bloc ^ K3

    # ── Round 2 inverse ───────────────────────────────────────────
    bloc = permuter(bloc, inverse=True)
    bloc = substituer_bloc(bloc, inverse=True)
    bloc = bloc ^ K2

    # ── Round 1 inverse ───────────────────────────────────────────
    bloc = permuter(bloc, inverse=True)
    bloc = substituer_bloc(bloc, inverse=True)
    bloc = bloc ^ K1

    return bloc


# ─── Chiffrement d'un message complet ────────────────────────────────────────

def chiffrer(message: str, cle: int) -> bytes:
    """
    - Chiffre un message texte complet avec SPNX-16.
    - Étapes :
        1. Convertir le texte en octets UTF-8
        2. Ajouter le padding
        3. Chiffrer chaque octet (bloc de 8 bits) indépendamment

    Args:
        message : str = le texte en clair
        cle     : int = clé de 16 bits (0 à 65535)

    Returns:
        bytes — le message chiffré
    """
    # Génération des sous-clés (une seule fois pour tout le message)
    sous_cles = key_schedule(cle)

    # Conversion + padding
    octets = message_vers_octets(message)
    octets = ajouter_padding(octets)

    # Chiffrement bloc par bloc
    chiffre = bytes(chiffrer_bloc(octet, sous_cles) for octet in octets)

    return chiffre


def dechiffrer(message_chiffre: bytes, cle: int) -> str:
    """
    - Déchiffre un message chiffré avec SPNX-16.
    - Étapes :
        1. Déchiffrer chaque octet indépendamment
        2. Retirer le padding
        3. Décoder les octets en texte UTF-8
    - Args:
         message_chiffre : bytes — le message chiffré
         cle             : int   — clé de 16 bits (0 à 65535)
    - Returns:
         str — le message déchiffré
    """
    sous_cles = key_schedule(cle)

    # Déchiffrement bloc par bloc
    octets = bytes(dechiffrer_bloc(octet, sous_cles) for octet in message_chiffre)

    # Retrait du padding + décodage
    octets = retirer_padding(octets)

    return octets_vers_message(octets)


# ─── Test rapide si lancé directement ────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("     RAPPORT CIPHER — SPNX-16")
    print("=" * 50)

    cle     = 0xABCD
    message = "Hello SPNX-16 !"

    # Chiffrement
    chiffre   = chiffrer(message, cle)
    dechiffre = dechiffrer(chiffre, cle)

    print(f"\n  Clé           : 0x{cle:04X} ({cle:016b})")
    print(f"  Message clair : {repr(message)}")
    print(f"  Chiffré (hex) : {chiffre.hex()}")
    print(f"  Déchiffré     : {repr(dechiffre)}")
    print(f"\n  Réversibilité : {' OK' if dechiffre == message else ' ERREUR'}")

    # Test déterminisme
    chiffre2 = chiffrer(message, cle)
    print(f"  Déterminisme  : {' OK' if chiffre == chiffre2 else ' ERREUR'}")

    # Test sensibilité clé
    cle2     = cle ^ 1   # On change 1 seul bit de la clé
    chiffre3 = chiffrer(message, cle2)
    print(f"  Sensib. clé   : {' OK' if chiffre != chiffre3 else ' ERREUR'}")

    print("=" * 50)