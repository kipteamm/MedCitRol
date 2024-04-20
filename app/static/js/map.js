const mapContainer = document.getElementById('map-container');
const canvas = document.getElementById("map");
const ctx = canvas.getContext('2d');

const tileSize = 16;
const mapWidth = 75;
const mapHeight = 75;

let zoom = tileSize * 4;
let camX = mapWidth / 2;
let camY = mapHeight / 2;

let terrain = [];
let buildings = [];

const terrainTileSet = new Image();

terrainTileSet.src = `/static/images/tilesets/${settlement.colour}_tilemap.png`;

terrainTileSet.onload = function() {
    loadTerrain();

    prepareCanvas();
};

function customRandom(seed) {
    let state = seed;

    return function() {
        const r = Math.sin(state++) * 10000;
        return r - Math.floor(r);
    };
}

seedData = customRandom(world.id)

function loadTerrain() {
    for (let x = 0; x < mapWidth; x++) {
        let column = [];
        for (let y = 0; y < mapHeight; y++) {
            const tileData = tiles.find(tile => tile.pos_x == x && tile.pos_y == y)

            if (tileData !== undefined) {
                column.push(tileData.tile_index);
            } else {
                column.push(Math.floor(seedData() * (6 - 3)) + 3);
            }
        }
        terrain.push(column);
    }
}

function prepareCanvas() {
    canvas.width = mapContainer.clientWidth;
    canvas.height = mapContainer.clientHeight;

    ctx.imageSmoothingEnabled = false;

    render();
};

window.onresize = prepareCanvas;

function getScreenX(x) {
    return Math.round((x - camX) * zoom) + canvas.width / 2;
}

function getScreenY(y) {
    return Math.round((y - camY) * -zoom) + canvas.height / 2;
}

function getWorldX(screenX) {
    return (screenX - canvas.width / 2) / zoom + camX;
}

function getWorldY(screenY) {
    return (screenY - canvas.height / 2) / -zoom + camY;
}

function getScreenWidth(width) {
    return width * zoom;
}

function getScreenHeight(height) {
    return height * zoom;
}

function drawTilesetImage(tileset, tileIndex, x, y, tileSize, scale) {
    const row = Math.floor(tileIndex / 6);

    ctx.drawImage(
        tileset,
        (tileIndex - (row * 6)) * tileSize,
        row * tileSize,
        tileSize,
        tileSize,
        Math.round(getScreenX(x)),
        Math.round(getScreenY(y)),
        getScreenWidth(scale),
        getScreenHeight(scale)
    );
}

function render() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    let startX = Math.floor(getWorldX(0)) - 1;
    let startY = Math.floor(getWorldY(canvas.height)) - 1;
    if (startX < 0) startX = 0;
    if (startY < 0) startY = 0;
    
    let endX = Math.ceil(getWorldX(canvas.width)) + 1;
    let endY = Math.ceil(getWorldY(0)) + 1;
    if (endX > mapWidth) endX = mapWidth;
    if (endY > mapHeight) endY = mapHeight;

    for (let x = startX; x < endX; x++) {
        for (let y = startY; y < endY; y++) {
            let tile = terrain[x][y];

            // Check if the tile is within the map bounds
            drawTilesetImage(terrainTileSet, tile, x, y, tileSize, 1);
        }
    }
}

const informationPanel = document.getElementById("information-panel");

let activeTile = null;
let isDragging = false;
let building = null;
let startX, startY;

canvas.addEventListener('click', (event) => handleClick(event, false));
canvas.addEventListener('contextmenu', (event) => handleClick(event, true));

function handleClick(event, rightClick=false) {
    if (isDragging) return;

    const worldX = getWorldX(event.offsetX);
    const worldY = getWorldY(event.offsetY);
    
    const tileX = Math.floor(worldX);
    const tileY = Math.floor(worldY) + 1;
    
    if (tileX < 0 || tileX > mapWidth || tileY < 0 || tileY > mapHeight) return;

    if ([3, 4, 5].includes(terrain[tileX][tileY])) {
        if (building === null) return;
        if (rightClick) {
            const buildingPlace = buildings.find(tile => tile.pos_x === tileX && tile.pos_y === tileY);

            if (buildingPlace === undefined) return;

            buildings.splice(buildings.indexOf(buildingPlace), 1);
            
            building.updateAmount(building, +1);

            return drawTilesetImage(terrainTileSet, terrain[tileX][tileY], tileX, tileY, tileSize, 1);
        }
        if (building.amount == 0) return;
        if (buildings.some(building => building.pos_x === tileX && building.pos_y === tileY)) return;

        building.updateAmount(building, -1);

        buildings.push({pos_x: tileX, pos_y: tileY, tile_type: building.item_type, character: character.id});

        return drawTilesetImage(terrainTileSet, building.tile_index, tileX, tileY, tileSize, 1);
    }

    if (rightClick) return;

    tile = tiles.find(tile => tile.pos_x === tileX && tile.pos_y === tileY)

    console.log(tile)

    informationPanel.classList.add("active")

    if (tile.id !== activeTile) {
        activeTile = tile.id;

        informationPanel.appendChild(informationComponent(tile));
    }
}

// Start dragging
canvas.addEventListener('mousedown', startDragging);
canvas.addEventListener('touchstart', startDragging);

function startDragging(e) {
    if (building !== null) return;

    e.preventDefault();
    isDragging = true;
    startX = e.clientX || e.touches[0].clientX;
    startY = e.clientY || e.touches[0].clientY;

    if (informationPanel.classList.contains("active")) {
        informationPanel.classList.remove("active");

        activeTile = null;

        informationPanel.innerHTML = '';
    }
}

// Stop dragging
canvas.addEventListener('mouseup', stopDragging);
canvas.addEventListener('mouseleave', stopDragging);
canvas.addEventListener('touchend', stopDragging);
canvas.addEventListener('touchcancel', stopDragging);

function stopDragging(e) {
    if (building !== null) return;

    e.preventDefault();
    isDragging = false;
}

// Drag the map
canvas.addEventListener('mousemove', dragMap);
canvas.addEventListener('touchmove', dragMap);

const dragSpeed = 1.15; 

function dragMap(e) {
    if (building !== null) return;

    e.preventDefault();
    if (isDragging) {
        const x = e.clientX || e.touches[0].clientX;
        const y = e.clientY || e.touches[0].clientY;
        const deltaX = (x - startX) * dragSpeed;
        const deltaY = (y - startY) * dragSpeed;
        startX = x;
        startY = y;
        camX -= deltaX / zoom;
        camY += deltaY / zoom;
        render(); // Redraw the map based on the new translation
    }
}

// canvas cancel rightclick
canvas.oncontextmenu = function(event) {event.preventDefault(); return;};

function centerCamera() {
    camX = mapWidth / 2;
    camY = mapHeight / 2;

    render();
}

// building
function build(tileX, tileY) {
    drawTilesetImage(terrainTileSet, 35, tileX, tileY, tileSize, 1);
}