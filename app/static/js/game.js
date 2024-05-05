const clockElement = document.getElementById('clock');
const dateElement = document.getElementById('date');

const night = document.getElementById('night');

function updateClock(timestamp) {
    const hours = new Date(timestamp * 1000).getHours();
    
    clockElement.innerText = `${String(hours).padStart(2, '0')}:00`;

    if (hours == 20) {
        night.classList.remove("no-delay");
        night.classList.add("active");
    } else if (hours > 19 || hours < 6) {
        night.classList.add("no-delay");
        night.classList.add("active");
    } else {
        night.classList.remove("no-delay");
        night.classList.remove("active")
    }
}

const sleepTimer = document.getElementById('sleep-timer');

function updateDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const dateString = date.toLocaleDateString('nl-BE', { day: 'numeric', month: 'long', year: 'numeric' });

    if (character.asleep) {
        let hours = date.getHours();
        hours = hours > 6? 6 + 24 - hours: 6 - hours;

        sleepTimer.innerText = hours === 0? 'soon' : hours === 1? `1 minute`: `${hours} minutes`;
    }

    dateElement.innerHTML = dateString;
}

updateClock(world.current_time)
updateDate(world.current_time)