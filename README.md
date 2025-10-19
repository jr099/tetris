# Tetris

Ce dépôt propose une implémentation simplifiée de Tetris en Python avec gestion des profils, des scores, une interface en ligne de commande et un tableau de bord web prêt pour un déploiement sur un hébergement Hostinger (Passenger + application WSGI minimale).

## Structure du projet

```
├── data/                  # Fichiers persistants (profils et scores)
├── app.py                 # Application WSGI minimale pour Hostinger
├── passenger_wsgi.py      # Point d'entrée WSGI pour Passenger
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

## Installation et exécution locale

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

## Déploiement sur Hostinger

L'hébergeur mutualisé Python de Hostinger repose sur Passenger et attend une application WSGI. Le dépôt inclut tout le nécessaire pour cette configuration.

1. **Préparer l'environnement**

   - (Optionnel) Créez un environnement virtuel sur l'hébergement :

     ```bash
     python3 -m venv ~/tetris-venv
     source ~/tetris-venv/bin/activate
     ```

   - Positionnez la variable d'environnement `TETRIS_DATA_FILE` vers un emplacement persistant (par exemple `~/tetris-data/profiles.json`). Passenger peut la définir via le fichier `.bash_profile` ou le panneau Hostinger.

2. **Déployer les fichiers**

   - Copiez l'ensemble du dépôt dans le dossier `~/domains/<votre-domaine>/public_python/` (ou le dossier configuré par Hostinger pour votre application Python).
   - Vérifiez que `passenger_wsgi.py` est à la racine de ce dossier et pointe vers `app.py`.

3. **Redémarrer Passenger**

   - Depuis le panneau de contrôle Hostinger, redémarrez l'application. Passenger détectera `passenger_wsgi.py` et importera `application`.

4. **Tester l'API**

   - Ouvrez `https://<votre-domaine>/` pour voir le tableau de bord (scores + profils).
   - Utilisez les endpoints REST pour gérer l'application :

     ```bash
     curl -X POST https://<votre-domaine>/api/profiles -H 'Content-Type: application/json' -d '{"name": "Alice"}'
     curl -X POST https://<votre-domaine>/api/scores -H 'Content-Type: application/json' -d '{"profile": "Alice", "score": 12345, "lines": 40}'
     curl https://<votre-domaine>/api/scores
     ```

Le jeu CLI peut continuer à être utilisé en parallèle pour jouer localement ; il suffit de synchroniser les scores vers l'API web si vous souhaitez centraliser les résultats.
