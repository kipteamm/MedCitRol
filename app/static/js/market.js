const marketPanel = document.getElementById("market-panel");
const marketContent = marketPanel.querySelector('.content');
const marketSell = document.getElementById("market-sell");

let updateSellables = true;
let marketItems = [];
let market = "settlement";

if (settlement.merchant) {
    document.getElementById("merchant-market-btn").style.display = "inline-block";
}

function switchMarket(marketType) {
    market = marketType;

    document.querySelector('.market-btn:disabled').disabled = false;
    document.getElementById(`${marketType}-market-btn`).disabled = true;

    marketContent.innerHTML = '';

    return openMarket();
}

async function openMarket() {
    cancelBuild();
    closeWorkPopup();

    if (market === "settlement" || (market === "world" && tiles.some(tile => tile.tile_type === "market_stall" && tile.character_id === character.id))) {
        marketSell.style.display = "block";

        if (updateSellables) {
            marketSell.querySelector("#sellables").innerHTML = "";

            character.inventory.filter(item => !item.buildable).forEach(item => {
                marketSell.querySelector("#sellables").appendChild(supplyComponent(item))
            })

            updateSellables = false;
        }
    } else {
        marketSell.style.display = "none";
    }

    marketPanel.classList.add("active");

    const response = await fetch(market === "merchant"? "/api/merchant" : `/api/market/${market}`, {
        method: "GET",
        headers: {
            "Authorization" : getCookie("psk"),
        }
    });

    const json = await response.json();

    if (!response.ok) {
        sendAlert("error", json.error);
    
        return;
    }

    let items = json;

    if (market === "merchant") {
        items = json.items;
    }

    if (items.length === 0 && settlement.traderoutes.length === 0) {
        marketContent.innerHTML = "You have no global trade partners.";

        return;
    }

    if (items.length === 0) {
        marketContent.innerHTML = "Nothing for sale right now! Come back later.";

        return;
    }

    marketContent.innerHTML = '';

    items.forEach(item => {
        marketItems.push(item);

        marketContent.appendChild(marketItemComponent(item));
    });
}

function closeMarket() {
    marketPanel.classList.remove("active");

    marketItems = [];
}

const itemInput = document.getElementById("item");
const amountInput = document.getElementById("amount");
const priceInput = document.getElementById("price");

async function sellItem() {
    const inventoryItem = character.inventory.find(item => item.item_type === itemInput.value);

    if (!inventoryItem) return;
    if (inventoryItem.amount < amountInput.value) return sendAlert("error", `You only have ${inventoryItem.amount} ${inventoryItem.item_type}.`);
    if (isNaN(priceInput.value)) return sendAlert("error", "Price must be a number.");

    const response = await fetch(`/api/market/${market}/sell`, {
        method: "POST",
        body: JSON.stringify({item_type: inventoryItem.item_type, amount: amountInput.value, price: priceInput.value}),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
        }
    })

    const json = await response.json();

    if (!response.ok) {
        sendAlert("error", json.error);
    
        return;
    }

    const existingMarketItem = document.getElementById(json.id);

    if (existingMarketItem !== null) {
        marketContent.replaceChild(marketItemComponent(json), existingMarketItem);
    } else {
        if (marketContent.querySelectorAll(".market-item").length === 0) {
            marketContent.innerHTML = '';
        }

        marketContent.appendChild(marketItemComponent(json));
    }
}

async function buyItem(id) {
    if (!isNaN(id)) {
        id = parseInt(id)
    }

    const marketItem = marketItems.find(item => item.id === id);

    if (!marketItem) return;
    if (marketItem.price > character.pennies) return sendAlert("error", "You don't have enough money.");

    updateProperty("pennies", -marketItem.price, false);

    marketItem.amount -= 1;

    if (marketItem.amount === 0) {
        document.getElementById(id).style.display = "none";
    } else {
        document.getElementById(`amount-${id}`).innerText = amountComponent(marketItem.amount);
    }

    sendAlert("success", "Your purchase was successful.")

    const response = await fetch(market === "merchant"? "/api/merchant/buy" : `/api/market/${market}/buy`, {
        method: "POST",
        body: JSON.stringify({item_id: marketItem.id}),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
        }
    })

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        if (marketItem.amount === 0) {
            document.getElementById(id).style.display = "block";
        }

        marketItem.amount += 1;

        document.getElementById(`amount-${id}`).innerText = amountComponent(marketItem.amount);

        updatePennies("pennies", marketItem.price, false);
    
        return;
    }

    return;
}

async function loadWarehouse(warehouseId) {
    const response = await fetch(`/api/warehouse/${warehouseId}`, {
        method: "GET",
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
        }
    })

    const json = await response.json();

    if (!response.ok) {
        sendAlert("error", json.error);

        return;
    }

    const content = informationPanel.querySelector("#warehouse-items")

    if (json.length === 0) {
        content.innerHTML = 'Warehouse is empty.'

        return;
    }

    json.forEach(item => {
        content.appendChild(supplyComponent(item))
    })
}
