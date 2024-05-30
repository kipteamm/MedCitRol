const workContent = document.getElementById('work-content');
const workPanel = document.getElementById('work-panel');
const workPopup = document.getElementById('work-popup');

const economyValue = 100;

let activeTask = null;
let activeTaskJson = null;

function work() {
    cancelBuild();
    closeMarket();

    if (workPopup.classList.contains("active")) {
        closeWorkPopup();

        return;
    }

    if (character.profession === "unemployed") {
        workPanel.classList.add("active");

        if (settlement.value < economyValue) return chooseProfession(3);

        return chooseProfession(8);
    }

    const shouldBuild = character.inventory.some(item => item.buildable === true && item.amount > 0);

    if (!shouldBuild) {
        if (character.profession === 'farmer' || character.profession === 'goldsmith' || character.profession === 'merchant' || character.profession === 'weaver') return loadTask();
        if (character.profession === 'miller' && character.inventory.some(item => item.item_type === "rye" && item.amount > 3)) return loadTask();
        if (character.profession === 'baker' && character.inventory.some(item => item.item_type === "rye_flour" && item.amount > 12)) return loadTask();
    }

    workPopup.appendChild(workStatusComponent(shouldBuild));
    workPopup.classList.add("active");
}

function closeWorkPopup() {
    workPopup.classList.remove("active");
    workPopup.innerHTML = '';
}

// working
async function loadTask() {
    closeWorkPopup();

    workPanel.classList.add("active");

    if (activeTask === character.task_index) return;

    activeTask = character.task_index;
    
    const response = await fetch('/api/task', {
        method: "GET",
        headers: {
            "Authorization" : getCookie('psk'),
        }
    });

    const json = await response.json();

    if (!response.ok) {
        if (json.error === "You have no profession.") {
            if (settlement.value < economyValue) return chooseProfession(3);

            return chooseProfession(6);
        }

        if (json.error === "No task found.") {
            workContent.innerHTML = '<h2>There is nothing for you to do right now..</h2>'
        }

        workContent.innerHTML = '<h2>Come back later..</h2>'

        activeTask = null;

        sendAlert("error", json.error);

        return;
    }

    activeTaskJson = json;

    workContent.innerHTML = '';
    workContent.appendChild(taskComponent(json))
    workContent.innerHTML += '<button onclick="submitTask()">Submit</button>';
}

function stopWorking() {
    workPanel.classList.remove("active");

    workContent.innerHTML = '';

    activeTask = null;
}

// professions
let professions = ["Baker", "Miller", "Farmer", "Merchant", "Weaver", "Goldsmith"]

function chooseProfession(level) {
    const availableProfessions = professions.slice(0, level).reverse();

    workContent.classList.add("profession-selector")
    
    availableProfessions.forEach(profession => {
        workContent.appendChild(professionComponent(profession))
    })
}

async function updateProfession(profession) {
    const response = await fetch('/api/profession/set', {
        method: "PUT",
        body: JSON.stringify({profession: profession}),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie('psk')
        }
    });

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        return;
    }
    
    activeTask = null;
    
    workContent.classList.remove("profession-selector");
    
    return stopWorking();
}

async function submitTask() {
    const response = await fetch('/api/task/submit', {
        method: "POST",
        body: JSON.stringify(answers),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie('psk')
        }
    });

    const json = await response.json();

    if (!response.ok) {
        sendAlert("error", json.error);

        return;
    }

    sendAlert("error", json.status)

    workContent.innerHTML = '';

    activeTask = null;

    return stopWorking();
}

