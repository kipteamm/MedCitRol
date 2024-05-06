const socket = io();

socket.on('connect', function() {
    console.log('connect');

    socket.emit('join', {access_key : getCookie('psk'), user_id : userId, world_id : world.id, settlement_id : settlement.id, character_id: character.id}); // room=
})

socket.on('disconnect', function() {
    console.log('disconnect');
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
        const tileIndex = tiles.findIndex(_tile => _tile.id === tile.id)

        if (tileIndex === -1) {
            tiles.push(tile)
        } else {
            tiles[tileIndex] = tile;
        }
        
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
        inventory.splice(inventory.indexOf(inventoryItem), 1);
    }

    if (itemData.buildable && buildPanel.classList.contains("active")) {
        openBuildMenu(true);
    }

    updateSellables = true;
});

socket.on('update_character', function(data) {
    if (character.id !== data.id) return;

    for (const [key, value] of Object.entries(data)) {
        if (key === "id") continue;

        if (key === "asleep") {
            sleeping(value);

            continue;
        }

        if (key === "jailed") {
            jailed(value);

            continue;
        }

        if (key === "taxes") {
            taxes(value)

            continue;
        }
        
        updateProperty(key, value, true)
    }
});

socket.on('update_settlement', function(data) {
    if (settlement.id !== data.id) return;

    for (const [key, value] of Object.entries(data)) {
        settlement[key] = value;
    }
})

socket.on('new_settlement', function(data) {
    world.settlements.push(data);
})

socket.on('merchant_leave', function() {
    document.getElementById("merchant-market-btn").style.display = "none";
})

socket.on('merchant_visit', function() {
    document.getElementById("merchant-market-btn").style.display = "inline-block";

    sendAlert("success", "A merchant is in town.")
})

socket.on('close_eyes', function(data) {
    if (character.id !== data.id) return;

    closeEyes()
})

socket.on('alert', function(data) {
    if (data.id && character.id !== data.id) return;

    sendAlert(data.type, data.message)
})
