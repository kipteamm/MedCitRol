const clockElement = document.getElementById('clock');
const dateElement = document.getElementById('date');

const night = document.getElementById('night');

function updateClock(timestamp) {
    const hours = new Date(timestamp * 1000).getHours();
    
    clockElement.innerText = `${String(hours).padStart(2, '0')}:00`;

    if (hours == 22) {
        night.classList.remove("no-delay");
        night.classList.add("active");
    } else if (hours > 21 || hours < 5) {
        night.classList.add("no-delay");
        night.classList.add("active");
    } else {
        night.classList.remove("no-delay");
        night.classList.remove("active")
    }
}

let currentDate = null;

function updateDate(timestamp) {
    currentDate = new Date(timestamp * 1000);
    
    const dateString = currentDate.toLocaleDateString('nl-BE', { day: 'numeric', month: 'long', year: 'numeric' });

    if (character.asleep) {
        updateSleepTimer();
    }

    dateElement.innerHTML = dateString;
}

const sleepTimer = document.getElementById('sleep-timer');

function updateSleepTimer() {
    let hours = currentDate.getHours();

    hours = hours > 6? 6 + 22 - hours: 5 - hours;

    sleepTimer.innerText = hours === 0? 'soon' : hours === 1? `in 1 minute`: `in ${hours} minutes`;
}

updateClock(world.current_time)
updateDate(world.current_time)