const workContent = document.getElementById('work-content');
const workPanel = document.getElementById('work-panel');

let activeTask = null;
let activeTaskJson = null;

// working
async function work() {
    workPanel.classList.add("active");

    if (activeTask === character.task_index) return;

    activeTask = character.task_index;
    
    const response = await fetch('/api/task', {
        method: "GET",
        headers: {
            "Authorization" : getCookie("psk"),
        }
    });

    const json = await response.json();

    if (!response.ok) {
        if (json.error === "You have no profession.") {
            if (settlement.value < 200) return chooseProfession(3);

            return chooseProfession(8);
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
let professions = ["Farmer", "Miller", "Baker", "Merchant", "Shoemaker", "Tanner", "Weaver", "Birdcatcher"]

function chooseProfession(level) {
    const availableProfessions = professions.slice(0, level);

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
            "Authorization" : getCookie("psk")
        }
    });

    if (!response.ok) {
        const json = await response.json();

        sendAlert("error", json.error);

        return;
    }
    
    activeTask = null;
    
    workContent.classList.remove("profession-selector");

    return work();
}

async function submitTask() {
    console.log(answers)

    const response = await fetch('/api/task/submit', {
        method: "POST",
        body: JSON.stringify(answers),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
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

