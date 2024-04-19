async function addField(fieldType) {
    const response = await fetch("/api/task/field/add", {
        method: "POST",
        body: JSON.stringify({task_id: parseInt(getCookie('task')), field_type: fieldType}),
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

    return task.replaceChild(editableTaskFieldComponent(await response.json()), document.getElementById(`task-field-${fieldId}`));
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

    return task.replaceChild(editableTaskFieldComponent(await response.json()), document.getElementById(`task-field-${fieldId}`));
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

    return task.replaceChild(editableTaskFieldComponent(json), document.getElementById(`task-field-${json.id}`));
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

    return window.location.reload()
}