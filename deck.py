"""Deck model for a Scoundrel-style card game.

Only the deck lives here: what a card is, how the dungeon is built,
and how cards are drawn. Game rules (damage, weapon limits, potions)
belong elsewhere and should read from Card properties.
"""

import random
from collections import deque
from dataclasses import dataclass

# Display names for face ranks. Everything else displays as its number.
RANK_NAMES = {11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}

# Each suit carries its own color, role, and the ranks that exist in the deck.
# Red suits omit Jack/Queen/King (11-13) but keep the Ace (14).
SUITS = {
    "Hearts": {
        "color": "red",
        "role": "Healing",
        "ranks": [*range(2, 11), 14],
    },
    "Diamonds": {
        "color": "red",
        "role": "Weapon",
        "ranks": [*range(2, 11), 14],
    },
    "Clubs": {
        "color": "black",
        "role": "Monster",
        "ranks": list(range(2, 15)),
    },
    "Spades": {
        "color": "black",
        "role": "Monster",
        "ranks": list(range(2, 15)),
    },
}

# Cards whose effect overrides the generic "rank = value" behavior.
# The Ace of Diamonds needs no entry: as a weapon its strength is just 14.
SPECIAL_EFFECTS = {
    ("Hearts", 14): "full_heal",
}


@dataclass(frozen=True)
class Card:
    
    suit: str
    rank: int

    @property
    def color(self) -> str:
        return SUITS[self.suit]["color"]

    @property
    def role(self) -> str:
        return SUITS[self.suit]["role"]

    @property
    def value(self) -> int:
        """Numeric value used for damage, weapon strength, or healing."""
        return self.rank

    @property
    def effect(self):
        """Special effect name, or None for an ordinary card."""
        return SPECIAL_EFFECTS.get((self.suit, self.rank))

    @property
    def name(self) -> str:
        return f"{RANK_NAMES.get(self.rank, str(self.rank))} of {self.suit}"

    def __str__(self) -> str:
        return self.name


def build_cards() -> list[Card]:
    """Create every card the SUITS table describes (46 by default)."""
    return [
        Card(suit, rank)
        for suit, data in SUITS.items()
        for rank in data["ranks"]
    ]


class Deck:
    """The dungeon: draw from the front, return cards to the bottom."""

    def __init__(self, seed=None):
        self._rng = random.Random(seed)  # seedable for reproducible games
        cards = build_cards()
        self._rng.shuffle(cards)
        self._cards = deque(cards)

    def draw(self, n: int = 1) -> list[Card]:
        """Draw up to n cards from the front; fewer if the deck runs out."""
        return [self._cards.popleft() for _ in range(min(n, len(self._cards)))]

    def put_on_bottom(self, cards) -> None:
        """Send cards to the bottom (used when a room is avoided)."""
        self._cards.extend(cards)

    def __len__(self) -> int:
        return len(self._cards)


if __name__ == "__main__":
    deck = Deck(seed=42)
    cards = build_cards()

    # Sanity checks on the deck definition.
    assert len(cards) == 46, len(cards)
    assert len(set(cards)) == 46
    assert not any(
        c.color == "red" and c.rank in (11, 12, 13) for c in cards
    )
    assert sum(c.role == "Monster" for c in cards) == 26
    assert Card("Hearts", 14).effect == "full_heal"
    assert Card("Diamonds", 14).value == 14

    # Draw / bottom behavior.
    room = deck.draw(4)
    assert len(room) == 4 and len(deck) == 42
    deck.put_on_bottom(room)
    assert len(deck) == 46

    print("All checks passed. First room:", ", ".join(map(str, room)))