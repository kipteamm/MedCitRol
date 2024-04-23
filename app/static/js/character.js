function updateProperty(property, value, reset=false) {
    character[property] = reset? value : character[property] + value;

    document.getElementById(property).innerText = `${character[property]}${property === "pennies"? " penningen" : ""}`;
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

async function payTaxes() {
    const response = await fetch('/api/character/taxes/pay', {
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

    sendAlert("success", "You paid your taxes.");

    taxes(0);
}

const sleepOverlay = document.getElementById("sleep-overlay");

function sleeping(isSleeping) {
    if (isSleeping) {
        sleepOverlay.classList.add("active");
    } else {
        sleepOverlay.classList.remove("active");
    }
}

const jailOverlay = document.getElementById("jail-overlay");

function jailed(isJailed) {
    if (isJailed) {
        jailOverlay.classList.add("active");
    } else {
        jailOverlay.classList.remove("active");
    }
}


const taxesElement = document.getElementById("taxes");

function taxes(value) {
    if (value > 0) {
        taxesElement.parentNode.classList.add("active")
        taxesElement.innerHTML = `${value} penningen`

        return
    }
    
    taxesElement.parentNode.classList.remove("active")
}

const tiredOverlay = document.getElementById("tired-overlay");

function closeEyes() {
    tiredOverlay.classList.add("active");

    setTimeout(() => {
        tiredOverlay.classList.remove("active");

        setTimeout(() => {
            sendAlert("success", "<i>yaaaaawn</i>, you feel tired.")
        }, 500);
    }, 2000);
}

async function requestFreedom() {
    const response = await fetch('/api/character/freedom/request', {
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

    sendAlert("success", "Freedom granted.")

    return;
}

const revolutionPanel = document.getElementById("revolution-panel");

function toggleRevolution() {
    revolutionPanel.classList.toggle("active");
}