from django.db import transaction
from django.http import HttpRequest, HttpResponse, QueryDict, HttpResponseBadRequest
from django.shortcuts import render 
from django.db.models.query import QuerySet
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from random import shuffle
from .models import *

@require_http_methods(["GET"])
@login_required
def deck_builder(request: HttpRequest) -> HttpResponse:
    packs: QuerySet[Pack] = request.user.packs # pyright: ignore
    inventory_cards = Card.sort_items(request.user.inventory_cards.all()) # pyright: ignore

    # for testing purposes let everyone at least have a common pack
    if packs.first() is None:
        Pack.create(request.user, "C")
        packs: QuerySet[Pack] = request.user.packs # pyright: ignore

    context = {
            'packs': packs.all(),
            'inventory_cards': inventory_cards,
            }


    return render(request, 'deckBuilder.html', context=context)

@require_http_methods(["GET"])
@login_required
def play_war(request: HttpRequest) -> HttpResponse:
    return render(request, 'playWar.html')


####
# htmx partial views for interactive ui
####

@require_http_methods(["POST"])
@transaction.atomic
@login_required
def get_cards(request: HttpRequest) -> HttpResponse:
    data = QueryDict(request.body) # pyright: ignore
    pack_pk = data.get("pack")
    pack = Pack.objects.get(pk=pack_pk, user=request.user)

    # get the cards ensuring they are from the same pack
    pack_items: list[PackItem] = []
    for name in data.keys():
        try:
            int(name)
        except ValueError:
            continue
        try:
            pack_items.append(PackItem.objects.get(pk=name, pack=pack))
        except PackItem.DoesNotExist:
            pass

    # this should never happen unless someone messes with the request
    if len(pack_items) == 0:
        return HttpResponseBadRequest("Need at least one card selected")
    elif len(pack_items) > pack.amount_to_pick:
        return HttpResponseBadRequest("Picked too many cards!")

    # add the cards to the users inventory
    for pack_item in pack_items:
        new_inventory_card = InventoryItem(
                card=pack_item.card,
                user=request.user
                )
        new_inventory_card.save()
    pack.delete()

    # getting all the user cards to replace the inventory
    inventory_cards = Card.sort_items(request.user.inventory_cards.all()) # pyright: ignore
    context = {
            'inventory_cards': inventory_cards,
            }

    return render(request, "inventory.html", context=context)


@require_http_methods(["DELETE"])
@transaction.atomic
@login_required
def delete_pack(request: HttpRequest) -> HttpResponse:
    data = QueryDict(request.body) # pyright: ignore
    pack_pk = data.get("pack")
    pack = Pack.objects.get(pk=pack_pk, user=request.user)
    pack.delete()
    return HttpResponse()

@require_http_methods(["DELETE"])
@transaction.atomic
@login_required
def delete_card(request: HttpRequest) -> HttpResponse:
    data = QueryDict(request.body) # pyright: ignore
    card_item_pk = data.get("inventoryItem")
    card_item = InventoryItem.objects.get(pk=card_item_pk, user=request.user)
    other_card_items = InventoryItem.objects \
            .filter(user=request.user, card=card_item.card) \
            .exclude(pk=card_item_pk)
    first_card_item = other_card_items.first()

    card_item.delete()

    if first_card_item  is None:
        # there are no card items to re render so just return an empty response to replace the 
        #    card item with
        return HttpResponse()

    context = {
            "count": len(other_card_items),
            "card": first_card_item.card,
            "first_inventory_item": first_card_item,
            }
    return render(request, "inventoryCardContainer.html", context=context)

@require_http_methods(["POST"])
@transaction.atomic
@login_required
def new_war_game(request: HttpRequest) -> HttpResponse:
    # there is only easy for now but if you added difficulties then
    #    you could do it here
    user = User.objects.get(pk=request.user.pk)

    game = WarGame.generate_game(user) # pyright: ignore
    context = {
            'iteration': game.iterations.first()
            }
    return render(request, "warIteration.html", context=context)

@require_http_methods(["GET"])
@transaction.atomic
@login_required
def next_war_iteration(request: HttpRequest) -> HttpResponse:
    data = request.GET
    last_iteration_pk = data.get("warIterationPk")
    last_iteration = WarIteration.objects.get(pk=last_iteration_pk)
    war_game: WarGame = last_iteration.game
    next_iteration = WarIteration.objects.filter(game=war_game, index=last_iteration.index + 1).first()

    context = {
            'user_won': war_game.user_won,
            'iteration': next_iteration
            }
    return render(request, "warIteration.html", context=context)



### the added example we did together
@require_http_methods(["GET"])
@login_required
def user_deck(request: HttpRequest) -> HttpResponse:
    # SELECT * FROM Card
    cards = list(Card.objects.all())
    shuffle(cards)
    context = {
            'cards': cards
            }
    return render(request, 'deck.html', context=context)

@require_http_methods(["GET"])
@login_required
def sorted_deck(request: HttpRequest) -> HttpResponse:
    # SELECT * FROM Card
    cards = list(Card.objects.all())
    sorted_cards = Card.sort_cards(cards)
    context = {
            'cards': sorted_cards
            }
    return render(request, 'deck.html', context=context)
