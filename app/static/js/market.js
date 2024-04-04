const marketPanel = document.getElementById("market-panel");
const marketContent = marketPanel.querySelector('.content');

let marketItems = [];

async function openMarket() {
    cancelBuild()

    marketPanel.classList.add("active");

    const response = await fetch("/api/settlement/market", {
        method: "GET",
        headers: {
            "Authorization" : getCookie("psk")
        }
    });

    const json = await response.json();

    if (!response.ok) {
        marketContent.innerHTML = json.error;
    
        return;
    }

    marketContent.innerHTML = '';

    json.forEach(item => {
        marketItems.push(item);

        marketContent.appendChild(marketItemComponent(item));
    });
}

function closeMarket() {
    marketPanel.classList.remove("active");
}

const itemInput = document.getElementById("item");
const amountInput = document.getElementById("amount");
const priceInput = document.getElementById("price");

async function sellItem() {
    const inventoryItem = character.inventory.find(item => item.item_type === itemInput.value);

    if (!inventoryItem) return;
    if (inventoryItem.amount < amountInput.value) return;

    const response = await fetch("/api/settlement/market/sell", {
        method: "POST",
        body: JSON.stringify({item_type: inventoryItem.item_type, amount: amountInput.value, price: priceInput.value}),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
        }
    })

    const json = await response.json();

    if (!response.ok) {
        marketContent.innerHTML = json.error;
    
        return;
    }

    const existingMarketItem = document.getElementById(`market-item-${json.id}`);

    if (existingMarketItem !== null) {
        marketContent.replaceChild(marketItemComponent(json), existingMarketItem);
    } else {
        marketContent.appendChild(marketItemComponent(json));
    }
}

async function buyItem(id) {
    const marketItem = marketItems.find(item => item.id === id);

    if (!marketItem) return;
    if (marketItem.price > character.pennies) return;

    updateProperty("pennies", -marketItem.price, false);

    marketItem.amount -= 1;

    if (marketItem.amount === 0) {
        document.getElementById(`market-item-${id}`).style.display = "none";
    } else {
        document.getElementById(`amount-${id}`).innerText = `${marketItem.amount}x`;
    }

    const response = await fetch("/api/settlement/market/buy", {
        method: "POST",
        body: JSON.stringify({item_id: marketItem.id}),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
        }
    })

    if (!response.ok) {
        const json = await response.json();

        marketContent.innerHTML = json.error;

        if (marketItem.amount === 0) {
            document.getElementById(`market-item-${id}`).style.display = "block";
        }

        marketItem.amount += 1;

        document.getElementById(`amount-${id}`).innerText = `${marketItem.amount}x`;

        updatePennies("pennies", marketItem.price, false);
    
        return;
    }

    return;
}
