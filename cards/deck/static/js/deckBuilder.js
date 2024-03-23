/**
 * Function to open the pack after a delay.
 * @param {Event} event - The event object triggered by the click event.
 */
function openPack(event) {
    const packIconElement = event.target;
    packIconElement.classList.add("rotatePackOpen");
    // look up the dom for the parent with the class pack
    const packElement = packIconElement.closest(".pack");

    setTimeout(() => {
        packIconElement.style.display = "none";
        packIconElement.remove("rotatePackOpen");
        cardsContainer = packElement.querySelector(".cards");
        console.log(cardsContainer);
        cardsContainer.style.display = 'inline';
    }, 1000);
}

function toggleCardSelect(event) {
    const cardElement = event.currentTarget;
    const packContainer = cardElement.closest(".pack");
    const cardPk = cardElement.getAttribute("data-pk");
    const hiddenCheckBoxes = packContainer.querySelectorAll('input[type="checkbox"]');
    if(cardElement.classList.contains("cardSelect")) {
        cardElement.classList.remove("cardSelect");
        for (const checkBox of hiddenCheckBoxes) {
            if (checkBox.getAttribute("name") === cardPk) {
                checkBox.checked = false;
            }
        }
    } else {
        // ensure this selecitons does not exceed the amount they can pick
        //  for the pack
        const amountToPick = packContainer.getAttribute("data-amountToPick");
        let amountPicked = 0;

        for (const checkBox of hiddenCheckBoxes) {
            if (checkBox.checked) {
                amountPicked++;
            }
        }
        if(amountPicked < amountToPick) {
            cardElement.classList.add("cardSelect");
            for (const checkBox of hiddenCheckBoxes) {
                if (checkBox.getAttribute("name") === cardPk) {
                    checkBox.checked = true;
                }
            }
        }
    }
}

// add pack listeners
const packIcons = document.querySelectorAll(".packIcon")
for (const packIcon of packIcons) {
    packIcon.addEventListener('click', openPack)
}

// add card listeners
const cards = document.querySelectorAll(".cardIcon")
for (const card of cards) {
    card.addEventListener('click', toggleCardSelect);
}

function inventoryCardDragStartHandler(ev) {
    const rowId = ev.target.getAttribute("id")
    ev.dataTransfer.setData("text/plain", rowId);
}

function garbageCardDropHandler(ev) {
    const cardItemId = ev.dataTransfer.getData("text/plain");
    const cardItemElement = document.getElementById(cardItemId )
    htmx.trigger(cardItemElement, 'deleteItem');
}

function cardOver(ev) {
    ev.preventDefault();
    ev.dataTransfer.dropEffect = "move";
}
