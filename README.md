# Tetris

## 📖 Présentation du projet
Ce dépôt contient une implémentation moderne du jeu **Tetris** destinée à servir de support pédagogique et de bac à sable pour expérimenter différentes architectures logicielles. Le projet vise à fournir :

- Une interface en ligne de commande (CLI) pour lancer rapidement une partie ou exécuter des simulations.
- Une interface graphique (GUI) riche, responsive et adaptée aux résolutions modernes.
- Un moteur de jeu suffisamment modulaire pour accueillir de nouvelles mécaniques (pièces personnalisées, modes de jeu alternatifs, etc.).

## 🧩 Objectifs principaux
- Reproduire fidèlement les règles classiques de Tetris (SRS, gestion du hold, compte du score et des combos).
- Proposer un système de profils permettant d’enregistrer les préférences des joueur·euse·s.
- Persister les scores et statistiques pour suivre la progression et comparer différentes sessions de jeu.
- Faciliter l’extension du code via une architecture claire et documentée.

---

## 📦 Dépendances
Le projet est développé en **Python 3.11** et utilise les dépendances principales suivantes :

| Paquet | Rôle |
| ------ | ---- |
| `pygame` | Rendu graphique 2D et gestion des entrées clavier pour la GUI. |
| `typer` | Construction de la CLI riche et typée. |
| `rich` | Affichage coloré dans le terminal (menus, tableaux de scores). |
| `pydantic` | Validation et sérialisation des configurations et profils. |
| `sqlalchemy` | Persistance des scores dans une base SQLite embarquée. |
| `pytest` | Cadre de tests unitaires et fonctionnels. |

Toutes les dépendances sont regroupées dans le fichier `requirements.txt`. Vous pouvez les installer via `pip` ou `pipx` selon vos préférences.

```bash
python -m venv .venv
source .venv/bin/activate  # Sous Windows : .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt
```

> 💡 Astuce : si vous utilisez [Poetry](https://python-poetry.org/), un fichier `pyproject.toml` est également disponible pour gérer les dépendances et les scripts d’exécution.

---

## ⚙️ Configuration
Les paramètres par défaut sont stockés dans `config/settings.json`. Ce fichier contrôle notamment :

- Les options d’affichage (taille de la fenêtre, mode sombre, FPS).
- Les raccourcis clavier pour les actions principales.
- Les préférences globales (vitesse de chute initiale, gravité douce, rotation guidée, etc.).

Vous pouvez fournir un fichier de configuration personnalisé à la CLI (`--config chemin/vers/fichier.json`) ou placer un fichier `settings.local.json` dans le dossier `config/` pour surcharger la configuration par défaut.

---

## 🚀 Installation et lancement
### Interface en ligne de commande (CLI)
```bash
# Lister les sous-commandes disponibles
tetris --help

# Lancer une partie rapide avec la configuration par défaut
tetris play --profile "Invité"

# Démarrer une session en mode marathon avec un niveau initial spécifique
tetris play --mode marathon --level 5

# Consulter le classement des scores
tetris scores top --limit 20
```

### Interface graphique (GUI)
```bash
# Lancer l’interface graphique
python -m tetris.gui

# Spécifier une configuration alternative
python -m tetris.gui --config config/settings.tournoi.json
```

Assurez-vous que le dossier `assets/` (polices, sons, sprites) est accessible ; il est chargé automatiquement par le module `tetris.assets`.

---

## 👤 Gestion des profils
Les profils utilisateur·rice sont gérés par le module `tetris.profiles` et stockés dans `data/profiles.json`.

- **Création** : via la CLI `tetris profile create --name "Alex" --theme neon --das 90`. Un identifiant unique est généré automatiquement.
- **Mise à jour** : `tetris profile edit --name "Alex" --das 100` pour ajuster la vitesse de déplacement.
- **Suppression** : `tetris profile delete --name "Invité"` retire un profil et réassigne ses scores au profil *Guest*.
- **Sélection dans la GUI** : l’écran d’accueil propose une liste déroulante pour choisir le profil actif ; les préférences (thème, commandes alternatives, etc.) sont appliquées immédiatement.

Les profils sont sérialisés via `pydantic` et validés à chaque lecture/écriture. Toute corruption détectée entraîne la création d’une sauvegarde automatique avant tentative de réparation.

---

## 🏆 Persistance des scores
Les scores sont gérés par `tetris.scores` qui s’appuie sur une base SQLite stockée dans `data/tetris.sqlite`.

- Chaque partie sauvegarde : le profil, le mode de jeu, le score final, la durée, le nombre de lignes complétées et le niveau maximal atteint.
- Des vues matérialisées facilitent le calcul des classements (top global, top par profil, meilleurs combos).
- La CLI expose `tetris scores export --format csv` pour exporter l’historique, et `tetris scores reset` pour repartir à zéro.

Les migrations de schéma sont automatisées via `alembic`. Avant chaque lancement, le moteur vérifie que la base est à jour (`alembic upgrade head`).

---

## 🕹️ Règles du jeu
L’implémentation suit les règles du *Tetris Guideline* :

1. **Système de rotation (SRS)** : rotation incrémentale avec *wall kicks*.
2. **Gestion du hold** : une seule pièce stockée, échange possible une fois par chute.
3. **RNG à sac de 7** : distribution équilibrée des tétriminos.
4. **Notation** :
   - Ligne simple : 100 points × multiplicateur de niveau.
   - Ligne double : 300 points × multiplicateur.
   - Ligne triple : 500 points × multiplicateur.
   - Tetris : 800 points × multiplicateur.
   - T-Spin et combos ajoutent des bonus.
5. **Gravité et accélération** : vitesse de chute augmentant tous les 10 niveaux, *soft drop* et *hard drop* disponibles.
6. **Fin de partie** : lorsqu’une nouvelle pièce ne peut plus être générée, le jeu se termine et le score est enregistré.

Des modes supplémentaires (marathon, sprint, ultra) sont implémentés via des variantes de règles dans `tetris.modes`.

---

## 🛠️ Architecture & contribution
### Structure des modules
```
tetris/
├── assets/             # Ressources statiques (sprites, polices, effets sonores)
├── config/             # Fichiers de configuration (settings.json, overrides locaux)
├── data/               # Profils, base SQLite et autres données persistantes
├── engine/             # Boucle de jeu, gestion des pièces, plateau, collisions
├── interfaces/
│   ├── cli.py          # Entrée principale de la CLI (Typer)
│   └── gui.py          # Application Pygame
├── modes/              # Variantes de gameplay (marathon, sprint, ultra…)
├── profiles.py         # Gestion des profils utilisateur·rice
├── scores.py           # Persistance et requêtes de scores
└── tests/              # Suite de tests Pytest
```

### Conventions de code
- **Style** : respect du standard [PEP 8](https://peps.python.org/pep-0008/) avec `ruff` pour la vérification automatique.
- **Typage** : annotations Python obligatoires sur les nouvelles fonctions/méthodes. `mypy` est exécuté dans l’intégration continue.
- **Docstrings** : format Google (triple guillemets, sections `Args`, `Returns`, `Raises`).
- **Commits** : respecter la convention [Conventional Commits](https://www.conventionalcommits.org/).

### Workflow de contribution
1. **Forker** le dépôt et créer une branche descriptive (`feature/ajout-mode-ultra`).
2. **Installer** les dépendances de développement :
   ```bash
   pip install -r requirements-dev.txt
   ```
3. **Lancer** les tests et les linters :
   ```bash
   pytest
   ruff check tetris
   mypy tetris
   ```
4. **Soumettre** une Pull Request en détaillant le contexte, la solution et les tests effectués.

Les Git hooks fournis dans `.githooks/` permettent d’automatiser `ruff` et `pytest` avant chaque commit. Activez-les avec :
```bash
git config core.hooksPath .githooks
```

---

## 🧪 Tests
La suite de tests `pytest` est organisée par fonctionnalité (engine, interfaces, profils, scores). Chaque module expose des *fixtures* pour construire rapidement des instances valides du moteur ou des tétriminos.

Pour exécuter les tests :
```bash
pytest
```

Pour un rapport de couverture HTML :
```bash
pytest --cov=tetris --cov-report=html
```

Des tests de snapshot CLI sont fournis via `pytest-approvaltests` afin d’assurer la stabilité des commandes. Les tests GUI utilisent `pytest-xvfb` pour tourner en environnement headless.

---

## 🤝 Support & FAQ
- **Questions rapides** : ouvrez une *Discussion* GitHub.
- **Bugs** : créez un ticket en précisant votre OS, la version de Python et les logs.
- **Idées de fonctionnalités** : soumettez une *feature request* en décrivant le comportement attendu et les contraintes envisagées.

Bon jeu !
