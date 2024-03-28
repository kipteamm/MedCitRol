const mapContainer = document.getElementById('map-container');
const canvas = document.getElementById("map");
const ctx = canvas.getContext('2d');

const zoomFactor = 4;
const tileSize = 16;
const mapWidth = 100;
const mapHeight = 100;

let translateX = 0;
let translateY = 0;

let terrain = []

const terrainTileSet = new Image();

terrainTileSet.src = '/static/images/tilesets/terrain.png';

terrainTileSet.onload = function() {
    loadTerrain();

    prepareCanvas();
};

function loadTerrain() {
    for (let x = 0; x < mapWidth; x++) {
        let column = [];
        for (let y = 0; y < mapHeight; y++) {
            column.push(Math.floor(Math.random() * (7 - 4)) + 4);
        }
        terrain.push(column);
    }
}

function prepareCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    ctx.imageSmoothingEnabled = false;

    render();
};

function render() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Get the visible portion of the map
    const visibleTilesX = Math.ceil(canvas.width / (tileSize * zoomFactor));
    const visibleTilesY = Math.ceil(canvas.height / (tileSize * zoomFactor));

    // Calculate the start position based on the translation
    const startX = Math.max(0, Math.floor(-translateX / tileSize));
    const startY = Math.max(0, Math.floor(-translateY / tileSize));

    for (let x = startX; x < startX + visibleTilesX; x++) {
        for (let y = startY; y < startY + visibleTilesY; y++) {
            let tile;

            if (x == 50 && y == 50) {
                tile = 2
            } else {
                tile = terrain[x][y]
            }

            // Calculate the position to draw the tile based on translate
            const drawX = (x * tileSize + translateX); // So your code might look like something like this
            const drawY = (y * tileSize + translateY);

            // Check if the tile is within the map bounds
            if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight) {
                ctx.drawImage(
                    terrainTileSet,
                    (tile - 1) * tileSize,
                    0,
                    tileSize,
                    tileSize,
                    drawX * zoomFactor - canvas.width / 2,
                    drawY * zoomFactor - canvas.height / 2,
                    tileSize * zoomFactor,
                    tileSize * zoomFactor
                );
            }
        }
    }
}

// Initialize dragging variables
let isDragging = false;
let startX, startY;

// Start dragging
canvas.addEventListener('mousedown', startDragging);
canvas.addEventListener('touchstart', startDragging);

function startDragging(e) {
    e.preventDefault();
    isDragging = true;
    startX = e.clientX || e.touches[0].clientX;
    startY = e.clientY || e.touches[0].clientY;
}

// Stop dragging
canvas.addEventListener('mouseup', stopDragging);
canvas.addEventListener('mouseleave', stopDragging);
canvas.addEventListener('touchend', stopDragging);
canvas.addEventListener('touchcancel', stopDragging);

function stopDragging(e) {
    e.preventDefault();
    isDragging = false;
}

// Drag the map
canvas.addEventListener('mousemove', dragMap);
canvas.addEventListener('touchmove', dragMap);

const dragSpeed = 0.5; 

function dragMap(e) {
    e.preventDefault();
    if (isDragging) {
        const x = e.clientX || e.touches[0].clientX;
        const y = e.clientY || e.touches[0].clientY;
        const deltaX = (x - startX) * dragSpeed;
        const deltaY = (y - startY) * dragSpeed;
        startX = x;
        startY = y;
        translateX += deltaX;
        translateY += deltaY; 
        render(); // Redraw the map based on the new translation
    }
}

function centerCamera() {
    translateX = -mapWidth / 2 * tileSize;
    translateY = -mapHeight / 2 * tileSize;

    render();
}