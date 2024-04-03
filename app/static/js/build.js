const buildPanel = document.getElementById('build-panel');

function openBuildMenu() {
    closeMarket()

    buildPanel.classList.add('active');

    const content = buildPanel.querySelector('.content');

    if (content.classList.contains("loaded")) return;

    content.innerHTML = '';

    character.inventory.forEach(item => {
        if (item.buildable) {
            content.appendChild(inventoryItem(item, true));
        }
    });

    content.classList.add("loaded");
}

function selectItem(id) {
    document.querySelector(`.inventory-item.active`)?.classList.remove("active");

    const item = document.getElementById(id);

    item.classList.add("active");

    building = character.inventory.find(item => item.id === id);
    building.updateAmount = (item, amount) => updateAmount(item, amount);
    building.initial_amount = building.amount;
}

function updateAmount(item, amount) {
    item.amount += amount;

    document.getElementById(`count-${item.id}`).innerText = `${item.amount}x`;
}

function confirmBuild() {
    if (buildings.length === 0) return;

    send('build', buildings)

    buildPanel.classList.remove('active');

    document.querySelector(`.inventory-item.active`)?.classList.remove("active");

    build = null;

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