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
    const response = fetch('/api/character/sleep')
}