const clockElement = document.getElementById('clock');
const dateElement = document.getElementById('date');

function updateClock(timestamp) {
    const date = new Date(timestamp * 1000);
    
    clockElement.innerText = `${String(date.getHours()).padStart(2, '0')}:00`
}

function updateDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const dateString = date.toLocaleDateString('nl-BE', { day: 'numeric', month: 'long', year: 'numeric' });

    dateElement.innerHTML = dateString;
}

updateClock(world.current_time)
updateDate(world.current_time)