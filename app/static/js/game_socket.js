const socket = io();

socket.on('connect', function() {
    socket.emit('join', {access_key : getCookie('psk'), world_id : world.id, settlement_id : settlement.id, character_id: character.id});
})

socket.on('update_time', function(data) {
    updateClock(data.current_time);
    updateDate(data.current_time);
})

socket.on('new_tile', function(data) {
    tiles.push(data);

    terrain[data.pos_x][data.pos_y] = data.tile_index;

    drawTilesetImage(terrainTileSet, data.tile_index, data.pos_x, data.pos_y, tileSize, 1);
})

socket.on('update_tile', function(data) {
    terrain[data.pos_x][data.pos_y] = data.tile_index;

    drawTilesetImage(terrainTileSet, data.tile_index, data.pos_x, data.pos_y, tileSize, 1);
})