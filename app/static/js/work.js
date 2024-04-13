const workContent = document.getElementById('work-content');
const workPanel = document.getElementById('work-panel');

let activeTask = null;
let activeTaskJson = null;
let answers = [];

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
            return chooseProfession(2);
        }

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
    const availableProfessions = professions.slice(0, level + 1);

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
    const response = await fetch('/api/task/submit', {
        method: "POST",
        body: JSON.stringify({}),
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

    workContent.innerHTML = '';

    activeTask = null;

    return stopWorking();
}

function selectOption(fieldId, optionId) {
    const option = document.getElementById(`task-option-${optionId}`);

    let answer = answers.find(field => field.field_id === fieldId);

    if (!answer) {
        answer = { field_id: fieldId, content: [] };
        answers.push(answer);
    }

    const isMultipleChoice = activeTaskJson.fields.some(field => field.field_type === "multiplechoice" && field.id === fieldId);
    const isSelected = answer.content.includes(optionId);

    if (isMultipleChoice && answer.content.length > 0) {
        const previousOptionId = answer.content[0];
        document.getElementById(`task-option-${previousOptionId}`).classList.remove("active");
        answer.content = [optionId];
    } else if (isSelected) {
        answer.content.splice(answer.content.indexOf(optionId), 1);
    } else {
        answer.content.push(optionId);
    }

    option.classList.toggle("active", !isSelected);
}
