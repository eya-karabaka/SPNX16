# SPNX-16 — Substitution–Permutation Network eXtended

> Algorithme de chiffrement symétrique par blocs — Prototype académique Python 3

---

## Description

SPNX-16 est un algorithme de chiffrement par blocs basé sur une architecture
SPN (Substitution-Permutation Network), conçu et implémenté from scratch en
Python pur, sans aucune bibliothèque cryptographique externe.

**⚠️ Avertissement** : SPNX-16 est un prototype pédagogique uniquement.
Avec une clé de 16 bits (65 536 combinaisons), il est cassable en moins
d'une seconde. Ne jamais utiliser pour protéger des données réelles.

---

## Paramètres techniques

| Paramètre        | Valeur                        |
|------------------|-------------------------------|
| Taille de bloc   | 8 bits (1 octet)              |
| Taille de clé    | 16 bits (65 536 clés)         |
| Nombre de rounds | 4                             |
| Sous-clés        | K1 à K5                       |
| Langage          | Python 3.8+                   |
| Lib crypto       | Aucune (interdit)             |

---

## Structure des rounds

Round 1 à 3 : XOR(Ki) → S-Box × 2 → Permutation
Round 4 : XOR(K4) → S-Box × 2 → XOR(K5) whitening final

---

## Installation et Lancement

### Étape 1 — Ouvrir le terminal

Sur Windows : clique droit sur le dossier `spnx16` → "Ouvrir dans le terminal"
Ou manuellement :

cd C:\Users\USER\Documents\security_projects\spnx16


### Étape 2 — Installer les bibliothèques graphiques

> ⚠️ Cette étape est optionnelle.
> Elle est nécessaire uniquement pour afficher les graphiques
> dans l'onglet Analyse. Le chiffrement, le déchiffrement,
> les tests et l'attaque fonctionnent sans elle.

pip install matplotlib numpy


### Étape 3 — Lancer le projet

python main.py


L'interface graphique s'ouvre automatiquement.
Le terminal affiche une vérification de chaque module avant le lancement.

---

## Lancement

```bash
# Lancer l'interface graphique complète
python main.py

# Lancer uniquement le chiffrement
python core/cipher.py

# Lancer les tests
python tests/test_sbox.py
python tests/test_reversibilite.py
python tests/test_determinisme.py
python tests/test_sensibilite_cle.py
python tests/test_avalanche.py
python tests/test_lat.py

# Lancer l'analyse
python analysis/avalanche.py
python analysis/ddt.py
python analysis/plots.py
python analysis/lat.py

# Lancer l'attaque
python attack/bruteforce.py
```

---

## Structure des fichiers

spnx16/
├── core/
│ ├── sbox.py # S-Box bijective non-linéaire
│ ├── permutation.py # Table de permutation diffusante
│ ├── key_schedule.py # Dérivation K1–K5 par rotations RoL
│ ├── cipher.py # Moteur chiffrement/déchiffrement
│ └── padding.py # Gestion du padding PKCS#7 adapté
├── analysis/
│ ├── avalanche.py # Mesure effet avalanche
│ ├── ddt.py # Difference Distribution Table
| ├── lat.py # Linear Approximation Table
│ └── plots.py # Graphiques matplotlib
├── attack/
│ └── bruteforce.py # Force brute + extrapolation
├── gui/
│ └── app.py # Interface Tkinter 4 onglets
├── tests/
│ ├── test_sbox.py
│ ├── test_reversibilite.py
│ ├── test_determinisme.py
│ ├── test_sensibilite_cle.py
│ ├── test_avalanche.py
│ └── test_lat.py
├── rapport/ # Graphiques générés automatiquement
├── main.py # Point d'entrée principal
└── README.md


---

## Tests de validation 
|      Test         |         Condition de succès                          |
|-------------------|------------------------------------------------------|
| Réversibilité     | `dechiffrer(chiffrer(M,K),K) == M` sur 1000 cas      |
| Déterminisme      | Deux appels `chiffrer(M,K)` donnent le même résultat |
| Sensibilité clé   | `K ≠ K'` implique `chiffrer(M,K) ≠ chiffrer(M,K')`   |
| Effet avalanche   | Moyenne entre 40% et 60% sur 2000 essais             |
| Bijectivité S-Box | `len(set(SBOX)) == 16`                               |

---

## Projet

- **Club**      : SECURINETS FST
- **Projet réalisé par** : Eya Karabaka
- **Encadrant** : Chahine Ben Salah
- **Langage**   : Python 3.8+

