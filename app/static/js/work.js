const workContent = document.getElementById('work-content');
const workPanel = document.getElementById('work-panel');

let activeTask;

// working
async function work() {
    workPanel.classList.add("active");

    if (activeTask === character.task_index) return;

    activeTask = character.task_index;
    
    const response = await fetch('/api/work', {
        method: "GET",
        headers: {
            "Authorization" : getCookie("psk"),
        }
    });

    const json = await response.json();

    if (!response.ok) {
        if (json.error === "You have no profession.") {
            return chooseProfession(4);
        }

        workContent.innerHTML = json.error;

        return;
    }

    workContent.appendChild(taskComponent(json))
}

function stopWorking() {
    workPanel.classList.remove("active");
}

// professions
let professions = ["Farmer", "Miller", "Baker", "Stonemason", "Woodcutter", "Carpenter", "Shoemaker", "Blacksmith", "Tailor", "Armourer", "Merchant"]

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

        workContent.innerHTML = json.error;

        return;
    }
    
    activeTask = null;

    return work();
}