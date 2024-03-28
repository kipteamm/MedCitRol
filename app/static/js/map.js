const canvas = document.getElementById("map");
const ctx = canvas.getContext('2d');

const terrainTileSet = new Image();
terrainTileSet.src = '/static/images/tilesets/terrain.png';

terrainTileSet.onload = function() {
    loadTerrain()
};

const zoomFactor = 4;

const map = {
    cols: 8,
    rows: 8,
    tsize: 16,
    tiles: [
      8, 3, 3, 3, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1,
      1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1,
      1, 1, 2, 1, 1, 1, 1, 1, 1, 5, 5, 1, 1, 1,
    ],
    getTile(col, row) {
      return this.tiles[row * map.cols + col];
    },
};

function loadTerrain() {
    canvas.width = map.cols * map.tsize * zoomFactor;
    canvas.height = map.rows * map.tsize * zoomFactor;

    ctx.imageSmoothingEnabled = false;

    for (let c = 0; c < map.cols; c++) {
        for (let r = 0; r < map.rows; r++) {
            const tile = map.getTile(c, r);
            
            ctx.drawImage(
                terrainTileSet, // image
                (tile - 1) * map.tsize, // source x
                0, // source y
                map.tsize, // source width
                map.tsize, // source height
                c * map.tsize * zoomFactor, // target x
                r * map.tsize * zoomFactor, // target y
                map.tsize * zoomFactor, // target width
                map.tsize * zoomFactor, // target height
            );
        }
    }
}
