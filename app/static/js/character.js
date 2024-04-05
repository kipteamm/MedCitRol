function updateProperty(property, value, reset=false) {
    character[property] = reset? value : character[property] + value;

    document.getElementById(property).innerText = `${character[property]}`;
}

async function eat() {
    const response = fetch('/api/character/eat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    });

    if (!response.ok) {
        return;
    }
}

async function sleep() {
    const response = fetch('/api/character/sleep')
}