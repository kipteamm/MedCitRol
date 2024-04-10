function updateProperty(property, value, reset=false) {
    character[property] = reset? value : character[property] + value;

    document.getElementById(property).innerText = `${character[property]}`;
}

async function eat() {
    const response = await fetch('/api/character/eat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    });

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        return;
    }
}

async function sleep() {
    const response = await fetch('/api/character/sleep', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    });

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        return;
    }
}

const sleepOverlay = document.getElementById("sleep-overlay");

function sleeping(isSleeping) {
    if (isSleeping) {
        sleepOverlay.classList.add("active");
    } else {
        sleepOverlay.classList.remove("active");
    }
}

const taxesElement = document.getElementById("taxes");

function taxes(value) {
    if (value > 0) {
        sendAlert("error", `Your ruler requested ${value} pennies in taxes.`);

        taxesElement.classList.add("active")

        return
    }
    
    taxesElement.classList.remove("active")
}