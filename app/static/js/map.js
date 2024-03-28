const mapContainer = document.getElementById('map-container');
const canvas = document.getElementById("map");
const ctx = canvas.getContext('2d');

const terrainTileSet = new Image();
terrainTileSet.src = '/static/images/tilesets/terrain.png';

terrainTileSet.onload = function() {
    loadTerrain();
    prepareCanvas();
};

const zoomFactor = 4;
const tileSize = 16;
const mapWidth = 100; // Number of tiles in the map horizontally
const mapHeight = 100; // Number of tiles in the map vertically

// Store the translate coordinates
let translateX = 0;
let translateY = 0;

let terrain = []

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

    // Update the rendered tiles when the user scrolls or drags the map
    canvas.addEventListener('scroll', render);
};

function render() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Get the visible portion of the map
    const visibleTilesX = Math.ceil(canvas.width / (tileSize * zoomFactor));
    const visibleTilesY = Math.ceil(canvas.height / (tileSize * zoomFactor));
    const offsetX = Math.floor(canvas.scrollLeft / (tileSize * zoomFactor));
    const offsetY = Math.floor(canvas.scrollTop / (tileSize * zoomFactor));

    // Calculate the start position based on the translation
    const startX = Math.max(0, Math.floor(-translateX / (tileSize * zoomFactor)));
    const startY = Math.max(0, Math.floor(-translateY / (tileSize * zoomFactor)));

    for (let x = startX; x < startX + visibleTilesX; x++) {
        for (let y = startY; y < startY + visibleTilesY; y++) {
            const tile = terrain[x][y]

            // Calculate the position to draw the tile based on translate
            const drawX = (x * tileSize + translateX) * zoomFactor;
            const drawY = (y * tileSize + translateY) * zoomFactor;

            // Check if the tile is within the map bounds
            if (x >= 0 && x < mapWidth && y >= 0 && y < mapHeight) {
                ctx.drawImage(
                    terrainTileSet,
                    (tile - 1) * tileSize,
                    0,
                    tileSize,
                    tileSize,
                    drawX,
                    drawY,
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
        mapContainer.scrollLeft += -deltaX;
        mapContainer.scrollTop += -deltaY;
        render(); // Redraw the map based on the new translation
    }
}
