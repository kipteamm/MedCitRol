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

function updateDate(timestamp) {
    const date = new Date(timestamp * 1000);
    const dateString = date.toLocaleDateString('nl-BE', { day: 'numeric', month: 'long', year: 'numeric' });

    dateElement.innerHTML = dateString;
}

const alertElement = document.getElementById('alert')

let alertActive = false;

function sendAlert(type, text) {
    const wordsPerMinute = text.split(/\s+/).length;
    const delay = Math.max((wordsPerMinute / 125) * 60 * 1000, 1500);
    
    if (alertActive) {
        setTimeout(() => {
            sendAlert(type, text);
        }, delay + 500);

        return
    }

    alertElement.innerHTML = `
        <div class="icon alert-icon"></div>
        <div class="alert-${type}">
            ${text}
        </div>
    `;

    alertElement.classList.add('show');

    alertActive = true;

    setTimeout(() => {
        alertElement.classList.remove('show');
        alertActive = false;
    }, delay);
}

updateClock(world.current_time)
updateDate(world.current_time)