const marketPanel = document.getElementById("market-panel");
const marketContent = marketPanel.querySelector('.content');

function openMarket() {
    marketPanel.classList.add("active");
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

    const response = await fetch("api/settlement/market/sell", {
        method: "POST",
        data: JSON.stringify({item_type: inventoryItem.item_type, amount: amountInput.value, price: priceInput.value}),
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

    marketContent.appendChild(marketItemComponent(json))
}