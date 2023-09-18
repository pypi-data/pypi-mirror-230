
# PokerHistoryReader

## Description

`PokerHistoryReader` est une bibliothèque Python conçue pour extraire et analyser des informations à partir d'historiques de mains de poker. Le package vous permet d'obtenir des données détaillées sur chaque main, comme les joueurs impliqués, les actions prises, les cartes tirées, et bien plus encore.

## Fonctionnalités

- Extraction du type de jeu (CashGame ou Tournoi)
- Identification des joueurs (Siège, Pseudo, Stack, Bounty)
- Actions des joueurs (Mise, Relance, Check, etc.)
- Extraction des cartes (Flop, Turn, River)
- Identification des gagnants et des pots remportés
- ... et bien d'autres !

## Prérequis

- Python 3.x
- AWS S3 (si vous souhaitez utiliser les fonctionnalités liées à S3)

## Installation

Pour installer le package, vous pouvez utiliser pip :

```
pip install pkrhistoryreader
```

Ou, si vous avez cloné le dépôt :

```
cd PokerHistoryReader
pip install .
```

## Utilisation

Après l'installation, vous pouvez utiliser le package comme suit :

```python
from pkrhistoryreader.reader import HistoryReader

# Initialisez l'objet
reader = HistoryReader()

# Utilisez les méthodes pour extraire des informations
game_type = reader.extract_game_type(hand_txt)
players_info = reader.extract_players(hand_txt)
# ... et ainsi de suite
```

## Documentation

Une documentation complète est à venir
## Contribution

Si vous souhaitez contribuer au projet, n'hésitez pas à ouvrir des issues ou à proposer des pull requests.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE.txt](LICENSE.txt) pour plus de détails.
