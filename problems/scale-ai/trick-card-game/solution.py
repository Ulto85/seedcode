"""Card / Deck / Player model plus a Game loop. Each trick costs O(hand size) to pick cards, so a full game is
O(N^2 / 4) for N cards, which is tiny for a 52-card deck. Space O(N)."""

RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
SUITS = ["C", "D", "H", "S"]
POINTS = {"5": 5, "10": 10, "K": 10}


class Card:
    def __init__(self, text):
        self.rank, self.suit = text[:-1], text[-1]
        self.r = RANKS.index(self.rank)
        self.s = SUITS.index(self.suit)

    @property
    def points(self):
        return POINTS.get(self.rank, 0)

    def sort_key(self):            # hand order: suit, then rank
        return (self.s, self.r)

    def __str__(self):
        return self.rank + self.suit


class Deck:
    def __init__(self, cards):      # cards are already shuffled (injected order)
        self.cards = [Card(c) for c in cards]

    def deal(self, players):
        for i, card in enumerate(self.cards):
            players[i % len(players)].hand.append(card)
        for p in players:
            p.sort_hand()


class Player:
    def __init__(self, idx):
        self.idx = idx
        self.hand = []
        self.points = 0

    def sort_hand(self):
        self.hand.sort(key=Card.sort_key)

    def lead(self):
        card = max(self.hand, key=lambda c: (c.r, -c.s))
        self.hand.remove(card)
        return card

    def follow(self, suit):
        same = [c for c in self.hand if c.suit == suit]
        if same:
            card = min(same, key=lambda c: c.r)
        else:
            card = min(self.hand, key=lambda c: (c.r, c.s))
        self.hand.remove(card)
        return card


class Game:
    def __init__(self, deck, n_players=4):
        self.players = [Player(i) for i in range(n_players)]
        Deck(deck).deal(self.players)
        self.leader = 0
        self.log = []

    def play_trick(self):
        n = len(self.players)
        lead_card = self.players[self.leader].lead()
        played = [(self.leader, lead_card)]
        for k in range(1, n):
            p = self.players[(self.leader + k) % n]
            played.append((p.idx, p.follow(lead_card.suit)))
        winner = max((pc for pc in played if pc[1].suit == lead_card.suit), key=lambda pc: pc[1].r)[0]
        self.players[winner].points += sum(c.points for _, c in played)
        self.log.append([self.leader, [str(c) for _, c in played], winner])
        self.leader = winner

    def play_all(self):
        while self.players[0].hand:
            self.play_trick()
        return self


def deal(deck):
    players = [Player(i) for i in range(4)]
    Deck(deck).deal(players)
    return [[str(c) for c in p.hand] for p in players]


def play_tricks(deck):
    return Game(deck).play_all().log


def score_game(deck):
    g = Game(deck).play_all()
    scores = [p.points for p in g.players]
    return {"scores": scores, "winner": scores.index(max(scores))}
