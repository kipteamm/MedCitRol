const workContent = document.getElementById('work-contnet');
const workPanel = document.getElementById('work-panel');

// working
async function work() {
    workPanel.classList.add("active");
    
    const response = await fetch('/api/work', {
        method: "GET",
        headers: {
            "Authorization" : getCookie("psk"),
        }
    });

    if (!response.ok) {
        try {
            const json = await response.json();

            if (json.error === "You have no profession.") {
                return chooseProfession(4);
            }

            workContent.innerHTML = json.error;
        } catch {
            alert("Unexpected error");
        }

        return;
    }

    workContent.innerHTML = await response.json();
}

function stopWorking() {
    workPanel.classList.remove("active");
}

// professions
let professions = ["Farmer", "Miller", "Baker", "Butcher", "Woodcutter", "Carpenter", "Stonemason", "Blacksmith", "Tailor", "Armourer", "Merchant"]

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
        try {
            const json = await response.json();

            workContent.innerHTML = json.error;
        } catch (error) {
            console.log(response, error)

            alert("Unexpected error");
        }

        return;
    }

    return work();
}