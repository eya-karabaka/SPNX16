# rapport/ — Graphiques générés par SPNX-16

Ce dossier reçoit automatiquement les graphiques produits
par le module analysis/plots.py lors de l'analyse.

## Fichiers générés

| Fichier                  | Description                              |
|--------------------------|------------------------------------------|
| avalanche_histogram.png  | Distribution de l'effet avalanche        |
| avalanche_par_bit.png    | Avalanche bit par bit                    |
| ddt_heatmap.png          | Heatmap de la DDT de la S-Box            |
| lat_heatmap.png          | Heatmap de la LAT de la S-Box            |

## Comment générer les graphiques

```bash
python analysis/plots.py
```

Ou depuis l'interface graphique :
    Onglet "Analyse" → boutons "Lancer Avalanche", "DDT"