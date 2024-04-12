function professionComponent(profession) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("profession");
    wrapper.innerHTML = `
        <img src="/static/images/professions/${profession.toLowerCase()}.webp">

        <h2>${profession}</h2>
    `;

    wrapper.onclick = function() {
        updateProfession(profession.toLowerCase());
    }

    return wrapper;
}

function taskComponent(task) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("task");
    
    task.fields.forEach(field => {
        wrapper.appendChild(taskFieldcomponent(field));
    })

    return wrapper;
}

let taskIndex = 1;

function taskFieldcomponent(taskField) {
    const wrapper = document.createElement("div");

    wrapper.id = `task-field-${taskField.id}`;
    wrapper.classList.add("task-field");
    wrapper.innerHTML = `<span>Vraag ${taskIndex}</span>`

    if (taskField.field_type === "text") {
        wrapper.innerHTML = `
            <p>${taskField.content? taskField.content : ""}</p>
        `;
    } else if (taskField.field_type === "image") {
        wrapper.innerHTML = `
            <img src="${taskField.content? `${taskField.content}?psk=${getCookie("psk")}` : "/static/images/assets/notfound.webp"}"/>
        `;
    } else if (taskField.field_type === "multiplechoice" || taskField.field_type === "checkboxes") {
        taskIndex++

        taskField.options.forEach(option => {
            wrapper.innerHTML += `
                <div>
                    ${option.content? option.content : ''}
                </div>
            `
        })
    }

    return wrapper;
}

function editableTaskFieldComponent(taskField) {
    const wrapper = document.createElement("div");

    wrapper.id = `task-field-${taskField.id}`;
    wrapper.classList.add("task-field");

    if (taskField.field_type === "text") {
        wrapper.innerHTML = `
            <textarea onchange="editField(${taskField.id}, this.value)">${taskField.content? taskField.content : ""}</textarea>
        `;
    } else if (taskField.field_type === "image") {
        wrapper.innerHTML = `
            <img src="${taskField.content? `${taskField.content}?psk=${getCookie("psk")}` : "/static/images/assets/notfound.webp"}"/>
        `;
    } else if (taskField.field_type === "multiplechoice" || taskField.field_type === "checkboxes") {
        taskField.options.forEach(option => {
            wrapper.innerHTML += `
                <div>
                    <input type="text" onchange="editOption(${option.id}, this.value)" value="${option.content? option.content : ''}"/>
                </div>
            `
        })

        wrapper.innerHTML += `
            <button onclick="addOption(${taskField.id})">Add option</button>
        `
    }

    return wrapper;
}

function inventoryItem(item, building) {
    const wrapper = document.createElement("div");

    wrapper.id = item.id;
    wrapper.classList.add("inventory-item");
    wrapper.innerHTML = `
        <b id="count-${item.id}">${item.amount}x</b> ${item.item_type}
    `;

    if (building) {
        wrapper.onclick = function() {selectItem(item.id)};
    }

    return wrapper;
}

function marketItemComponent(item) {
    const wrapper = document.createElement("div");

    wrapper.id = `market-item-${item.id}`;
    wrapper.classList.add("market-item");
    wrapper.innerHTML = `
        ${item.item_type}
        <b id="amount-${item.id}">${item.amount}x</b>
        <b>${item.price}pennies</b>
        ${item.character_id !== character.id? `<button onclick="buyItem('${item.id}')">Buy</button>` : ""}
    `;

    return wrapper;
}