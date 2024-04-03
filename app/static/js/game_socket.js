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
        tiles[tiles.findIndex(_tile => _tile.id === tile.id)] = tile;

        terrain[tile.pos_x][tile.pos_y] = tile.tile_index;

        drawTilesetImage(terrainTileSet, tile.tile_index, tile.pos_x, tile.pos_y, tileSize, 1);
    })
})

socket.on('update_inventory', function(data) {
    const itemData = data.item;
    const inventory = data.is_settlement ? settlement.inventory : character.inventory;

    let inventoryItem = inventory.find(item => item.id === itemData.item_id);

    if (!inventoryItem) {
        inventory.push(itemData);
    } else {
        inventoryItem.amount = itemData.amount;
    }
});

function send(event, data) {
    eventData = defaultData
    eventData.event_data = data

    socket.emit(event, eventData)
}