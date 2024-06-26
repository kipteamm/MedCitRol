const buildPanel = document.getElementById('build-panel');

function openBuildMenu(overWriteClose=false) {
    closeMarket();
    closeWorkPopup();
    toggleMap(true);

    if (!overWriteClose && buildPanel.classList.contains("active")) return cancelBuild();

    buildPanel.classList.add('active');

    const content = buildPanel.querySelector('.content');

    content.innerHTML = '';

    character.inventory.forEach(item => {
        if (item.buildable && item.amount > 0) {
            content.appendChild(inventoryItemComponent(item, true));
        }
    });
}

const buildInformation = document.getElementById('build-information');

function selectItem(id) {
    if (building === character.inventory.find(item => item.id === id) && buildings.length === 0) {
        document.querySelector(`.inventory-item.active`)?.classList.remove("active");
        buildInformation.style.display = 'none';

        building = null;

        return;
    }
    
    document.querySelector(`.inventory-item.active`)?.classList.remove("active");
    buildInformation.style.display = 'block';

    const item = document.getElementById(`id-${id}`);

    item.classList.add("active");

    building = character.inventory.find(item => item.id === id);
    building.updateAmount = (item, amount) => updateAmount(item, amount);
    building.initial_amount = building.amount;
}

const confirmBuildButton = document.getElementById('confirm-build-button');

function updateAmount(item, amount) {
    item.amount += amount;

    document.getElementById(`count-${item.id}`).innerText = `${item.amount}x`;
}

async function confirmBuild() {
    if (buildings.length === 0) return cancelBuild();

    const response = await fetch('/api/build', {
        method: 'PUT',
        body: JSON.stringify(buildings),
        headers: {
            'Authorization': `${getCookie('psk')}`,
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        return;
    }

    buildPanel.classList.remove('active');

    document.querySelector(`.inventory-item.active`)?.classList.remove("active");

    building = null;

    buildings = [];
}

function cancelBuild() {
    buildPanel.classList.remove('active');

    if (building !== null) {
        building.updateAmount(building, building.initial_amount - building.amount);

        building = null;
    }

    buildings.forEach(building => {
        drawTilesetImage(terrainTileSet, terrain[building.pos_x][building.pos_y], building.pos_x, building.pos_y, tileSize, 1);
    })

    document.querySelector(`.inventory-item.active`)?.classList.remove("active");

    buildings = [];
}

async function buyBuildable(type, price) {
    if (character.pennies < price) return sendAlert("error", "You don't have enough pennies.");

    const response = await fetch('/api/buildable/purchase', {
        method: "POST",
        body: JSON.stringify({item_type: type}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        return;
    }
}