# Tetris

Ce dépôt propose une implémentation simplifiée de Tetris en Python avec gestion des profils, des scores et une interface en ligne de commande.

## Structure du projet

```
├── data/                  # Fichiers persistants (profils et scores)
├── main.py                # Point d'entrée CLI
├── src/
│   └── tetris/
│       ├── __init__.py    # Export des éléments publics du paquet
│       ├── board.py       # Logique du plateau et gestion des lignes
│       ├── game.py        # Boucle de jeu et contrôle des pièces
│       ├── profiles.py    # Gestionnaire de profils avec persistance JSON
│       ├── scores.py      # Calculs de score et enregistrement
│       └── tetromino.py   # Définitions des formes et rotations
└── tests/
    ├── test_game.py       # Tests unitaires sur la logique de jeu et le scoring
    └── test_profiles.py   # Tests de persistance et de gestion des profils
```

## Installation et exécution

1. Créez un environnement virtuel et installez les dépendances nécessaires (uniquement `pytest` pour les tests) :

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install pytest
   ```

2. Lancez le jeu en mode interactif :

   ```bash
   python main.py
   ```

   L'interface vous permet de sélectionner ou créer un profil, de jouer en utilisant les commandes clavier et de consulter le tableau des scores.

3. Pour afficher uniquement les meilleurs scores :

   ```bash
   python main.py --scores
   ```

## Commandes dans le jeu

- `a` : déplacement vers la gauche
- `d` : déplacement vers la droite
- `s` : descente douce
- `w` : rotation horaire
- `espace` : chute directe (hard drop)
- `q` : quitter la partie en cours

Chaque ligne complétée applique les règles de scoring Tetris (simple, double, triple, Tetris) avec bonus de combo et points supplémentaires pour les descentes.

## Tests automatisés

Les tests couvrent :

- la rotation et l'insertion des pièces,
- l'effacement des lignes et la mise à jour du score,
- la création, la persistance et la sélection des profils.

Exécutez l'ensemble des tests avec :

```bash
pytest
```

Les tests utilisent un stockage temporaire afin de ne pas impacter les fichiers de données réels.
