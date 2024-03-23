from django.db import models
from django.db.models import Case, When, Value, IntegerField
from django.contrib.auth.models import User
from django.db import transaction
from dataclasses import dataclass
from random import randint, shuffle

from django.db.models.query import QuerySet


RANK_SUIT_TO_PATH = {
    '2': {
        'C': '2_of_clubs.png',
        'D': '2_of_diamonds.png',
        'H': '2_of_hearts.png',
        'S': '2_of_spades.png'
    },
    '3': {
        'C': '3_of_clubs.png',
        'D': '3_of_diamonds.png',
        'H': '3_of_hearts.png',
        'S': '3_of_spades.png'
    },
    '4': {
        'C': '4_of_clubs.png',
        'D': '4_of_diamonds.png',
        'H': '4_of_hearts.png',
        'S': '4_of_spades.png'
    },
    '5': {
        'C': '5_of_clubs.png',
        'D': '5_of_diamonds.png',
        'H': '5_of_hearts.png',
        'S': '5_of_spades.png'
    },
    '6': {
        'C': '6_of_clubs.png',
        'D': '6_of_diamonds.png',
        'H': '6_of_hearts.png',
        'S': '6_of_spades.png'
    },
    '7': {
        'C': '7_of_clubs.png',
        'D': '7_of_diamonds.png',
        'H': '7_of_hearts.png',
        'S': '7_of_spades.png'
    },
    '8': {
        'C': '8_of_clubs.png',
        'D': '8_of_diamonds.png',
        'H': '8_of_hearts.png',
        'S': '8_of_spades.png'
    },
    '9': {
        'C': '9_of_clubs.png',
        'D': '9_of_diamonds.png',
        'H': '9_of_hearts.png',
        'S': '9_of_spades.png'
    },
    '10': {
        'C': '10_of_clubs.png',
        'D': '10_of_diamonds.png',
        'H': '10_of_hearts.png',
        'S': '10_of_spades.png'
    },
    'A': {
        'C': 'ace_of_clubs.png',
        'D': 'ace_of_diamonds.png',
        'H': 'ace_of_hearts.png',
        'S': 'ace_of_spades.png'
    },
    'J': {
        'C': 'jack_of_clubs.png',
        'D': 'jack_of_diamonds.png',
        'H': 'jack_of_hearts.png',
        'S': 'jack_of_spades.png'
    },
    'K': {
        'C': 'king_of_clubs.png',
        'D': 'king_of_diamonds.png',
        'H': 'king_of_hearts.png',
        'S': 'king_of_spades.png'
    },
    'Q': {
        'C': 'queen_of_clubs.png',
        'D': 'queen_of_diamonds.png',
        'H': 'queen_of_hearts.png',
        'S': 'queen_of_spades.png'
    }
}

RANK_TO_VALUE = {

        }

RARIETY_TO_PATH = {
        'C': 'common.png',
        'U': 'uncommon.png',
        'R': 'rare.png',
        'L': 'legendary.png',
        }

COMMON_DISTRIBUTION = {
        '2': 2,
        '3': 2,
        '4': 2,
        '5': 2,
        '6': 1,
        '7': 1,
        '8': 1,
        '9': 1,
        '10': 1,
        'J': 0,
        'Q': 0,
        'K': 0,
        'A': 0,
        }

UNCOMMON_DISTRIBUTION = {
        '2': 10,
        '3': 10,
        '4': 10,
        '5': 10,
        '6': 10,
        '7': 10,
        '8': 10,
        '9': 10,
        '10': 10,
        'J': 5,
        'Q': 3,
        'K': 2,
        'A': 1,
        }

RARE_DISTRIBUTION = {
        '2': 1,
        '3': 1,
        '4': 1,
        '5': 1,
        '6': 3,
        '7': 5,
        '8': 5,
        '9': 5,
        '10': 5,
        'J': 4,
        'Q': 3,
        'K': 2,
        'A': 1,
        }

LEGENDARY_DISTRIBUTION = {
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
        '6': 0,
        '7': 0,
        '8': 0,
        '9': 0,
        '10': 0,
        'J': 10,
        'Q': 7,
        'K': 6,
        'A': 5,
        }

EVEN_SUIT_DISTRIBUTION = {
        'H': 1,
        'D': 1,
        'C': 1,
        'S': 1,
        }

@dataclass
class PlayCard:
    suit: str
    rank: str

    def get_path(self) -> str:
        return RANK_SUIT_TO_PATH[self.suit][self.rank]

    def as_card(self) -> 'Card':
        card, _ = Card.objects.get_or_create(rank=self.rank, suit=self.suit)
        return card


    def __str__(self) -> str:
        # lsp's can't really know there dynamically generated methods from pyright for
        #     choice feilds
        return f"{Card.get_suit_display(self.suit)} of {Card.get_rank_display(self.rank)}" # pyright: ignore

    # dunders for comparisons
    def __eq__(self, other):
        return self.rank == other.rank

    def __lt__(self, other: 'PlayCard'):
        return Card.RANK_TO_VALUE[self.rank] < Card.RANK_TO_VALUE[other.rank] 

    def __gt__(self, other: 'PlayCard'):
        return Card.RANK_TO_VALUE[self.rank] > Card.RANK_TO_VALUE[other.rank] 


class PackInfo:
    rank_distribution: dict[str, int]
    suit_distribution: dict[str, int]
    amount_to_pick: int
    amount_available: int

    def __init__(self, rariety: str):
        if rariety == 'C':
            self.rank_distribution = COMMON_DISTRIBUTION
            self.suit_distribution = EVEN_SUIT_DISTRIBUTION
            self.amount_to_pick = 5
            self.amount_available = 7
        elif rariety == 'U':
            self.rank_distribution = UNCOMMON_DISTRIBUTION
            self.suit_distribution = EVEN_SUIT_DISTRIBUTION
            self.amount_to_pick = 5
            self.amount_available = 10
        elif rariety == 'R':
            self.rank_distribution = RARE_DISTRIBUTION
            self.suit_distribution = EVEN_SUIT_DISTRIBUTION
            self.amount_to_pick = 8
            self.amount_available = 15
        elif rariety == 'L':
            self.rank_distribution = LEGENDARY_DISTRIBUTION
            self.suit_distribution = EVEN_SUIT_DISTRIBUTION
            self.amount_to_pick = 10
            self.amount_available = 20
        else:
            raise ValueError("Invalid rariety value")

    # creates a flat list of all the ranks/ suits and chooses a random index
    def pick_cards(self) -> list[PlayCard]:
        pack_cards: list[PlayCard] = []
        for _ in range(self.amount_available):
            flat_ranks = []
            for rank, count in self.rank_distribution.items():
                flat_ranks.extend([rank]*count)
            flat_suits = []
            for suit, count in self.suit_distribution.items():
                flat_suits.extend([suit]*count)
            # python's randint has inclusive bounds
            random_rank_index = randint(0, len(flat_ranks) - 1)
            random_suit_index = randint(0, len(flat_suits) - 1)
            pack_card = PlayCard(
                    rank=flat_ranks[random_rank_index],
                    suit=flat_suits[random_suit_index])
            pack_cards.append(pack_card)

        return pack_cards


# You could argue all cards should be made at the start
#    for 52 cards that makes a lot of sense but if we wanted to make
#    more attributes or bonuses the amount of cards would increase
#    exponentially
class Card(models.Model):
    # hearts, diamonds, clubs, and spades.
    SUITS = (
            ('H', 'Hearts'),
            ('D', 'Diamonds'),
            ('C', 'Clubs'),
            ('S', 'Spades'),
            )

    RANKS = (
            ('2', 'Two'),
            ('3', 'Three'),
            ('4', 'Four'),
            ('5', 'Five'),
            ('6', 'Six'),
            ('7', 'Seven'),
            ('8', 'Eighth'),
            ('9', 'Nine'),
            ('10', 'Ten'),
            ('J', 'Jack'),
            ('Q', 'Queen'),
            ('K', 'King'),
            ('A', 'Ace'),
            )

    RANK_TO_VALUE = {
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7,
            '9': 8,
            '10': 9,
            'J': 10,
            'Q': 11,
            'K': 12,
            'A': 13,
            }

    suit = models.CharField(max_length=2, choices=SUITS)
    rank = models.CharField(max_length=2, choices=RANKS)

    def get_path(self) -> str:
        return RANK_SUIT_TO_PATH[self.rank][self.suit]

    def get_sort_value(self) -> int:
        return Card.RANK_TO_VALUE[self.rank]

    @staticmethod
    def sort_cards(cards: list['Card']) -> list['Card']:
        sorted_cards = sorted(cards, key=lambda c: (c.suit, c.get_sort_value()), reverse=True)
        return sorted_cards

    @staticmethod
    def sort_items(items: list) -> list['Card']:
        sorted_items = sorted(items, key=lambda i: (i.card.suit, i.card.get_sort_value()), reverse=True)
        return sorted_items

    def __str__(self) -> str:
        # lsp's can't really know there dynamically generated methods from pyright for
        #     choice feilds
        return f"{self.get_rank_display()} of {self.get_suit_display()}" # pyright: ignore

# creating
class Pack(models.Model):
    rarieties = (
            ('C', 'Common'),
            ('U', 'Uncommon'),
            ('R', 'Rare'),
            ('L', 'Lengendary'),
            )
    rariety = models.CharField(max_length=2, choices=rarieties)
    amount_to_pick = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="packs")
    pack_items: models.QuerySet['PackItem']

    def get_path(self) -> str:
        return RARIETY_TO_PATH[self.rariety]

    def __str__(self) -> str:
        return self.get_rariety_display() # pyright: ignore

    # need to ensure packs that create a pack is atomic
    #    because if a pack was created and then something crashed
    #    in that instance the cards may not be made
    @transaction.atomic
    @staticmethod
    def create(user, rariety: str) -> 'Pack':
        pack_info = PackInfo(rariety)
        pack_cards = pack_info.pick_cards()
        pack = Pack(rariety=rariety, user=user, amount_to_pick=pack_info.amount_to_pick)
        pack.save()

        # create the pack items for the cards
        for pack_card in pack_cards:
            # want to get or create the new card created
            #    said before all cards are not created at the start
            #    bc im lazy and dont want to add another startup command
            #    and if we add more attributes to cards they will grow exponentially
            card, _ = Card.objects.get_or_create(
                    suit = pack_card.suit,
                    rank = pack_card.rank,
                    )
            pack_item = PackItem(
                    pack=pack,
                    card=card
                    )
            pack_item.save()

        return pack


# Groups the pack with a collection of cars
class PackItem(models.Model):
    pack = models.ForeignKey(Pack, related_name="pack_items", on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

# groups a user with a collection of cards
class InventoryItem(models.Model):
    user = models.ForeignKey(User, related_name="inventory_cards", on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)


# could add difficultys
#  done this way instead of just having the constant bc doing a round would
#  mutate the list
def get_easy_deck_difficulty() -> list[PlayCard]:
    EASY_DIFFICULTY_DECK: list[PlayCard] = [
            PlayCard(suit='C', rank='5'), PlayCard(suit='H', rank='5'), PlayCard(suit='S', rank='5'),
            PlayCard(suit='C', rank='6'), PlayCard(suit='H', rank='6'), PlayCard(suit='S', rank='6'),
            PlayCard(suit='C', rank='7'), PlayCard(suit='H', rank='7'), PlayCard(suit='S', rank='7'),
            PlayCard(suit='C', rank='8'), PlayCard(suit='H', rank='8'), PlayCard(suit='S', rank='8'),
            ]
    return EASY_DIFFICULTY_DECK

class WarGame(models.Model):
    user = models.ForeignKey(User, related_name="war_games", on_delete=models.CASCADE)
    user_won = models.BooleanField()

    iterations: QuerySet['WarIteration']

    @staticmethod
    @transaction.atomic
    def generate_game(user: User) -> 'WarGame':
        # use the users current cards to play the game
        inventory_items: list[PackItem] = list(user.inventory_cards.all()) #pyright: ignore
        # only take the first 26 cards of the user's shuffled deck
        shuffle(inventory_items)
        inventory_items = inventory_items[:min(26, len(inventory_items))]
        # translating them to PlayCards just to easily work with them and difficulty decks
        play_cards = []
        for inventory_item in inventory_items:
            card: Card = inventory_item.card 
            play_cards.append(PlayCard(suit=card.suit, rank=card.rank))

        game = WarGame(user=user, user_won=True)
        game.save()
        WarGame.play_round(
                first_deck=play_cards,
                second_deck=get_easy_deck_difficulty(),
                war_bounty=[],
                game=game,
                )
        if len(play_cards) == 0:
            game.user_won = False
            game.save()
        return game

    @staticmethod
    def play_round(first_deck: list[PlayCard], second_deck: list[PlayCard], war_bounty: list[PlayCard],
                   game: 'WarGame', index: int=0):
        # base case of recursion is one deck has been exhausted
        if len(first_deck) == 0 or len(second_deck) == 0:
            if len(war_bounty) > 0:
                print(war_bounty)
                print(first_deck)
                print(second_deck)
                raise ValueError("we messed up")
            return
        # game ends in a draw and it's assumed to repeat infinitely
        if index > 10_000:
            return

        new_round = WarIteration(game=game, index=index)
        new_round.save()
        index += 1
        first_deck_card = first_deck[0]
        second_deck_card = second_deck[0]
        # get cards in hand
        WarItem(iteration=new_round, card=first_deck_card.as_card(), css_class="inHand1").save()
        WarItem(iteration=new_round, card=second_deck_card.as_card(), css_class="inHand2").save()
        # there is a war bounty so make sure that a pile of something exists (does matter what card is)
        if len(war_bounty):
            WarItem(
                    iteration=new_round,
                    card=second_deck_card.as_card(),
                    css_class="inWarBounty",
                    is_face_down=True).save()
        if first_deck_card == second_deck_card:
            # move in hand cards to war bounty
            war_iteration1 = WarIteration(game=game, index=index)
            war_iteration1.save()
            WarItem(
                    iteration=war_iteration1,
                    card=first_deck_card.as_card(),
                    css_class="inHand1 toWarBounty").save()
            WarItem(
                    iteration=war_iteration1,
                    card=second_deck_card.as_card(),
                    css_class="inHand2 toWarBounty").save()
            index += 1
            # same card
            # playing the rule where their last card will act as the play war deciding card
            first_end_range = min(4, len(first_deck) - 1)
            second_end_range = min(4, len(second_deck) - 1)
            first_cards = first_deck[:first_end_range]
            second_cards = second_deck[:second_end_range]
            # get face down cards for war in hand
            war_iteration2 = WarIteration(game=game, index=index)
            war_iteration2.save()
            for _ in range(first_end_range - 1):
                WarItem(
                        iteration=war_iteration2,
                        card=first_deck_card.as_card(),
                        css_class="inHand1",
                        is_face_down=True).save()
            for _ in range(second_end_range - 1):
                WarItem(
                        iteration=war_iteration2,
                        card=first_deck_card.as_card(),
                        css_class="inHand2",
                        is_face_down=True).save()
            index += 1
            # move those face down cards in hand to war bounty
            war_iteration3 = WarIteration(game=game, index=index)
            war_iteration3.save()
            for _ in range(first_end_range - 1):
                WarItem(
                        iteration=war_iteration3,
                        card=first_deck_card.as_card(),
                        css_class="inHand1 toWarBounty",
                        is_face_down=True).save()
            for _ in range(second_end_range - 1):
                WarItem(
                        iteration=war_iteration3,
                        card=first_deck_card.as_card(),
                        css_class="inHand2 toWarBounty",
                        is_face_down=True).save()
            index += 1
            # add all their cards besides the possible play card (why we need the -1)
            war_bounty.extend(first_cards)
            war_bounty.extend(second_cards)
            # get rid of the cards from their deck
            first_deck = first_deck[first_end_range:]
            second_deck = second_deck[second_end_range:]
        # remove the played cards from the deck and add them to the
        #   the winning deck
        elif first_deck_card > second_deck_card:
            # moving cards in hand and possibly inbounty to winning deck
            normal_win = WarIteration(game=game, index=index)
            normal_win.save()
            WarItem(
                    iteration=normal_win,
                    card=first_deck_card.as_card(),
                    css_class="inHand1 toDeck1").save()
            WarItem(
                    iteration=normal_win,
                    card=second_deck_card.as_card(),
                    css_class="inHand2 toDeck1").save()
            if len(war_bounty):
                WarItem(
                        iteration=normal_win,
                        card=second_deck_card.as_card(),
                        css_class="inWarBounty toDeck1").save()
            index += 1
            # removing cards and adding to victor
            new_round.save()
            first_deck.pop(0)
            second_deck.pop(0)
            first_deck.extend(war_bounty)
            war_bounty = []
            first_deck.append(first_deck_card)
            first_deck.append(second_deck_card)
        elif first_deck_card < second_deck_card:
            # moving cards in hand and possibly inbounty to winning deck
            normal_win = WarIteration(game=game, index=index)
            normal_win.save()
            WarItem(
                    iteration=normal_win,
                    card=first_deck_card.as_card(),
                    css_class="inHand1 toDeck2").save()
            WarItem(
                    iteration=normal_win,
                    card=second_deck_card.as_card(),
                    css_class="inHand2 toDeck2").save()
            if len(war_bounty):
                WarItem(
                        iteration=normal_win,
                        card=second_deck_card.as_card(),
                        css_class="inWarBounty toDeck2").save()
            index += 1
            # removing cards and adding to victor
            first_deck.pop(0)
            second_deck.pop(0)
            second_deck.extend(war_bounty)
            war_bounty = []
            second_deck.append(first_deck_card)
            second_deck.append(second_deck_card)

        WarGame.play_round(first_deck, second_deck, war_bounty, game, index)


class WarIteration(models.Model):
    game = models.ForeignKey(WarGame, related_name="iterations", on_delete=models.CASCADE)
    index = models.IntegerField()
    items: QuerySet['WarItem']

    class Meta: #pyright: ignore
        ordering = ['index']

class WarItem(models.Model):
    iteration = models.ForeignKey(WarIteration, related_name="items", on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    is_face_down = models.BooleanField(default=False)
    css_class = models.CharField(max_length=50)



