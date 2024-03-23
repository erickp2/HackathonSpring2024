from django.urls import path
from .views import *

urlpatterns = [
        path('play_war', play_war, name='play_war'),
        path('deck_builder', deck_builder, name='deck_builder'),

        path('get_cards', get_cards, name='get_cards'),
        path('delete_pack', delete_pack, name='delete_pack'),
        path('delete_card', delete_card, name='delete_card'),
        path('new_war_game', new_war_game, name='new_war_game'),
        path('next_war_iteration', next_war_iteration, name='next_war_iteration'),

        ### added for example
        path('user_deck', user_deck, name='user_deck'),
        path('sorted_deck', sorted_deck, name='sorted_deck'),
]
