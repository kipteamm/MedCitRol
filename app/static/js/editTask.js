async function addField(fieldType) {
    const response = await fetch("/api/task/field/add", {
        method: "POST",
        body: JSON.stringify({task_id: getCookie('task'), field_type: fieldType}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    return task.appendChild(editableTaskFieldComponent(await response.json()));
}

async function editField(fieldId, value) {
    const response = await fetch("/api/task/field/edit", {
        method: "PATCH",
        body: JSON.stringify({field_id: fieldId, content: value}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    return task.replaceChild(editableTaskFieldComponent(await response.json()), document.getElementById(fieldId));
}

function handleImage(event) {
    const file = event.target.files[0];

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();

        reader.onload = function (e) {
            uploadFile(file)
        };

        reader.onerror = function (error) {
            sendAlert("error", `Error reading ${file.name}: ${error.message}`);
            checkAllImagesLoaded();
        };

        reader.readAsDataURL(file);
     } else {
        sendAlert("error", "Invalid file type.");
        checkAllImagesLoaded();
    }
}

async function uploadFile(file) {
    const formData = new FormData();

    formData.append('task_id', getCookie('task'));
    formData.append('image', file);
    
    const response = await fetch(`/api/task/image/add`, {
        method: 'POST',
        body: formData,
        headers: {
            "Authorization": getCookie("psk"),
        }
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    return task.appendChild(editableTaskFieldComponent(await response.json()));
}

async function addOption(fieldId) {
    const response = await fetch("/api/task/option/add", {
        method: "POST",
        body: JSON.stringify({field_id: fieldId}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    return task.replaceChild(editableTaskFieldComponent(await response.json()), document.getElementById(fieldId));
}

async function editOption(optionId, value) {
    const response = await fetch("/api/task/option/edit", {
        method: "PATCH",
        body: JSON.stringify({option_id: optionId, content: value}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    const json = await response.json();

    return task.replaceChild(editableTaskFieldComponent(json), document.getElementById(json.id));
}

async function updateAnswers(taskId) {
    const response = await fetch("/api/task/answers", {
        method: "PATCH",
        body: JSON.stringify({task_id: taskId, answers: answers}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    return window.location.reload();
}

let activeActions = null;
let activePositon = null

function showActions(field) {
    if (field.id === activeActions) return;

    const currentScrollPosition = window.scrollY || document.documentElement.scrollTop;

    activePositon = field.getBoundingClientRect().top + document.documentElement.scrollTop;

    document.getElementById("actions").style.top = `${currentScrollPosition > activePositon? currentScrollPosition : activePositon}px`;

    activeActions = field.id;
}

window.onscroll = function() {
    const currentScrollPosition = window.scrollY || document.documentElement.scrollTop;

    if (currentScrollPosition >= activePositon) {
        const actions = document.getElementById("actions")
        
        actions.classList.add("scroll");
        actions.style.top = `${activePositon}px`;
    } else {
        document.getElementById("actions").classList.remove("scroll");
    }
}

async function moveField(direction) {
    const field = document.getElementById(activeActions);

    if (direction === "up" && field.getAttribute("field-index") === "0") return console.log("1");
    if (direction === "down" && field.getAttribute("field-index") === (task.field_index - 1).toString()) return console.log("2");

    const fieldId = activeActions.split("-")

    const response = await fetch(`/api/task/field/move`, {
        method: "PATCH",
        body: JSON.stringify({field_id: fieldId, direction: direction}),
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    
    let otherElement;

    if (direction === "up") {
        otherElement = field.previousElementSibling;

        task.insertBefore(field, otherElement);
    } else {
        otherElement = field.nextElementSibling;

        otherElement.insertAdjacentElement("afterend", field);
    }

    old_index = field.getAttribute("field-index");
    new_index = otherElement.getAttribute("field-index");

    field.setAttribute("field-index", new_index);
    otherElement.setAttribute("field-index", old_index);

    showActions(otherElement);

    return;
}

async function duplicateField() {
    const fieldId = activeActions

    const response = await fetch(`/api/task/field/${fieldId}/duplicate`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    return task.appendChild(editableTaskFieldComponent(await response.json()));
}

async function deleteField() {
    const fieldId = activeActions

    const response = await fetch(`/api/task/field/${fieldId}/delete`, {
        method: "DELETE",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${getCookie('psk')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    const field = document.getElementById(fieldId);
    const nextSibling = field.nextElementSibling;
    const previousSibling = field.previousElementSibling
    
    field.remove();

    if (nextSibling) {
        showActions(nextSibling);
    } else {
        showActions(previousSibling);
    }

    return;
}
