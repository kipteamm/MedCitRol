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

    return task.replaceChild(editableTaskFieldComponent(await response.json()), document.getElementById(`task-${fieldId}`));
}


function handleFiles(files) {
    uploadLabel.style.display = 'none';
    spinner.style.display = 'block';

    let imagesLoaded = 0;

    function checkAllImagesLoaded() {
        imagesLoaded++;

        if (imagesLoaded === files.length) {
            spinner.style.display = 'none';
            uploadLabel.style.display = 'block';
        }
    }

    for (const file of files) {
        if (file.type.startsWith('image/')) {
            selectedFiles.push(file);

            const reader = new FileReader();

            reader.onload = function (e) {
                const preview = document.createElement('div');
                preview.classList.add('image');
                preview.classList.add('loading')

                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = file.name;

                preview.innerHTML = `
                    <span onclick="removeImage(this.parentNode)"><iconify-icon icon="fa6-solid:trash-can"></iconify-icon></span>
                    <iconify-icon icon="fa6-solid:spinner" class="spinner" id="spinner"></iconify-icon>
                `

                preview.appendChild(img);
                previewContainer.appendChild(preview);

                uploadFile(file, preview)

                checkAllImagesLoaded();
            };

            reader.onerror = function (error) {
                newAlert(`Error reading ${file.name}: ${error.message}`, "error");
                checkAllImagesLoaded();
            };

            reader.readAsDataURL(file);
        } else {
            newAlert("Invalid file type.", "error");
            checkAllImagesLoaded();
        }
    }
}

// Handle paste
document.addEventListener('paste', function (event) {
    const items = (event.clipboardData || event.originalEvent.clipboardData).items;

    for (const item of items) {
        if (item.kind === 'file') {
            const file = item.getAsFile();
            handleFiles([file]);
        }
    }
});

async function removeImage(elm) {
    const imgAlt = elm.querySelector('img').alt;

    selectedFiles = selectedFiles.filter(file => file.name !== imgAlt);

    elm.style.display = 'none';

    saveChangesButton.disabled = true;

    const response = await fetch(`/api/location/${locationId}/images/remove/${elm.id}`, {
        method: 'DELETE',
        headers: {
            "Authorization": getCookie("au_id"),
            "X-CSRFToken": getCookie("csrftoken"),
        }
    })

    saveChangesButton.disabled = false;

    if (!response.ok) {
        newAlert(await getError(response), "error");

        elm.style.display = 'flex';

        return;
    }

    elm.remove();

    return
}

// upload file to api
async function uploadFile(file, preview) {
    const formData = new FormData();

    formData.append('location_id', locationId);
    formData.append('image', file);

    saveChangesButton.disabled = true;

    const response = await fetch(`/api/location/${locationId}/images/add`, {
        method: 'POST',
        body: formData,
        headers: {
            "Authorization": getCookie("au_id"),
            "X-CSRFToken": getCookie("csrftoken")
        }
    })

    saveChangesButton.disabled = false;

    preview.classList.remove('loading')

    if (!response.ok) {
        newAlert(await getError(response), "error");

        preview.remove();

        return;
    }

    const json = await response.json();

    preview.id = json.id;

    return;
}