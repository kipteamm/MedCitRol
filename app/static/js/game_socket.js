const defaultData = {access_key : getCookie('psk'), world_id : world.id, settlement_id : settlement.id, character_id: character.id};
const socket = io();

socket.on('connect', function() {
    socket.emit('join', defaultData);
})

socket.on('update_time', function(data) {
    updateClock(data.current_time);
    updateDate(data.current_time);
})

socket.on('new_tiles', function(data) {
    data.forEach(tile => {
        tiles.push(tile);

        terrain[tile.pos_x][tile.pos_y] = tile.tile_index;

        drawTilesetImage(terrainTileSet, tile.tile_index, tile.pos_x, tile.pos_y, tileSize, 1);
    })
})

socket.on('update_tiles', function(data) {
    data.forEach(tile => {     
        tiles.find(_tile => _tile.id === tile.id).update(tile);

        terrain[tile.pos_x][tile.pos_y] = tile.tile_index;

        drawTilesetImage(terrainTileSet, tile.tile_index, tile.pos_x, tile.pos_y, tileSize, 1);
    })
})

function send(event, data) {
    eventData = defaultData
    eventData.event_data = data

    socket.emit(event, eventData)
}