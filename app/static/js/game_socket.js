const socket = io();

socket.on('connect', function() {
    socket.emit('join', {access_key : getCookie('psk'), world_id : world.id, settlement_id : settlement.id, character_id: character.id})
})

socket.on('update_time', function(data) {
    console.log(data)
})