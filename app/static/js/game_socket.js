const defaultData = {access_key : getCookie('psk'), world_id : world.id, settlement_id : settlement.id, character_id: character.id};
const socket = io();

socket.on('connect', function() {
    socket.emit('join', defaultData);
})

socket.on('disconnect', function() {
    return window.location.href = '/home';
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
        tiles[tiles.findIndex(_tile => _tile.id === tile.id)] = tile;

        terrain[tile.pos_x][tile.pos_y] = tile.tile_index;

        drawTilesetImage(terrainTileSet, tile.tile_index, tile.pos_x, tile.pos_y, tileSize, 1);
    })
})

socket.on('update_inventory', function(data) {
    if (data.character_id !== character.id && data.character_id !== null) return;

    const itemData = data.item;
    const inventory = data.settlement? settlement.inventory : character.inventory;
    const inventoryItem = inventory.find(item => item.id === itemData.id);

    if (!inventoryItem && !data.deleted) {
        inventory.push(itemData);
    } else if (!data.deleted) {
        inventoryItem.amount = itemData.amount;
    } else {
        inventory.splice(inventory.indexOf(inventoryItem), 1)
    }
});

socket.on('update_character', function(data) {
    if (character.id !== data.id) return;

    for (const [key, value] of Object.entries(data)) {
        if (key === "id") continue;
        
        updateProperty(key, value, true)
    }
});

function send(event, data) {
    eventData = defaultData
    eventData.event_data = data

    socket.emit(event, eventData)
}