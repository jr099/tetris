"""Simple command-line interface to play the Tetris game."""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from src.tetris.game import Game
from src.tetris.profiles import Profile, ProfileManager
from src.tetris.scores import ScoreManager


def render_board(game: Game) -> str:
    grid = game.current_board()
    lines = []
    border = "+" + "-" * game.board.width + "+"
    lines.append(border)
    for row in grid:
        line = "|" + "".join(cell[0] if cell else "." for cell in row) + "|"
        lines.append(line)
    lines.append(border)
    return "\n".join(lines)


def select_profile(manager: ProfileManager) -> Profile:
    while True:
        profiles = manager.list_profiles()
        if profiles:
            print("Profils existants :")
            for idx, profile in enumerate(sorted(profiles, key=lambda p: p.name), start=1):
                print(f"  {idx}. {profile.name} (meilleur score: {profile.best_score})")
        else:
            print("Aucun profil. Créons-en un !")
        choice = input("Entrez le numéro du profil, 'n' pour nouveau ou 'q' pour quitter : ").strip()
        if choice.lower() == "q":
            sys.exit(0)
        if choice.lower() == "n":
            name = input("Nom du nouveau profil : ").strip()
            if not name:
                print("Le nom ne peut pas être vide.")
                continue
            try:
                return manager.create_profile(name)
            except ValueError as exc:
                print(exc)
                continue
        if choice.isdigit() and profiles:
            index = int(choice) - 1
            if 0 <= index < len(profiles):
                profile = sorted(profiles, key=lambda p: p.name)[index]
                manager.set_active_profile(profile.name)
                return profile
        print("Choix invalide. Réessayez.")


def display_scores(manager: ProfileManager) -> None:
    print("\n=== Meilleurs scores ===")
    top = manager.top_scores()
    if not top:
        print("Aucun score enregistré pour le moment.")
        return
    for rank, entry in enumerate(top, start=1):
        print(f"{rank:>2}. {entry['profile']} - {entry['score']} pts ({entry['lines']} lignes)")
    print()


def run_game(profile: Profile, manager: ProfileManager) -> None:
    score_manager = ScoreManager(manager)
    game = Game(score_manager=score_manager)
    game.start(profile.name)

    print("\nCommandes : a= gauche, d= droite, s= descente, w= rotation, espace= chute, q= quitter")
    while not game.game_over and game.active:
        print(render_board(game))
        print(f"Score: {game.score_manager.score} | Lignes: {game.score_manager.total_lines}")
        command = input("Commande : ").strip().lower()
        if command == "a":
            game.move_left()
        elif command == "d":
            game.move_right()
        elif command == "s":
            moved = game.soft_drop()
            if not moved:
                game.tick()
        elif command == "w":
            game.rotate()
        elif command == " ":
            game.hard_drop()
        elif command == "q":
            game.game_over = True
            game.active = None
        else:
            print("Commande inconnue.")
            continue
        if command not in {"s", " ", "q"}:
            game.tick()

    try:
        snapshot = game.score_manager.finalize()
        print(f"Partie terminée ! Score: {snapshot.score} | Lignes: {snapshot.lines}")
    except RuntimeError:
        print("Aucun profil actif, le score n'a pas été enregistré.")



def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Tetris sur terminal")
    parser.add_argument("--scores", action="store_true", help="Afficher le tableau des scores et quitter")
    args = parser.parse_args(argv)

    manager = ProfileManager()
    if args.scores:
        display_scores(manager)
        return 0

    profile = manager.get_active_profile()
    if not profile:
        profile = select_profile(manager)
    else:
        answer = input(f"Profil actif : {profile.name}. Voulez-vous en choisir un autre ? (o/N) ").strip().lower()
        if answer == "o":
            profile = select_profile(manager)
    manager.set_active_profile(profile.name)

    display_scores(manager)
    run_game(profile, manager)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
