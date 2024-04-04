const clockElement = document.getElementById('clock');
const dateElement = document.getElementById('date');

const night = document.getElementById('night');

function updateClock(timestamp) {
    const hours = new Date(timestamp * 1000).getHours();
    
    clockElement.innerText = `${String(hours).padStart(2, '0')}:00`;

    if (hours > 20) {
        night.classList.add('active');
    } else if (hours > 6) {
        night.classList.remove('active');
    }
}

function updateDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const dateString = date.toLocaleDateString('nl-BE', { day: 'numeric', month: 'long', year: 'numeric' });

    dateElement.innerHTML = dateString;
}

updateClock(world.current_time)
updateDate(world.current_time)