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

    if (taskField.field_type === "header") {
        wrapper.innerHTML = `
            <h2>${taskField.content? taskField.content : ""}</h2>
        `;
    } else if (taskField.field_type === "text") {
        wrapper.innerHTML = `
            <p>${taskField.content? taskField.content.replace(/\n+/g, '</p><p>') : ""}</p>
        `;
    } else if (taskField.field_type === "image") {
        wrapper.appendChild(imageComponent(taskField.content? `${taskField.content}?psk=${getCookie("psk")}` : "/static/images/assets/notfound.webp"))
    } else if (taskField.field_type === "multiplechoice" || taskField.field_type === "checkboxes" || taskField.field_type === "connect") {
        taskIndex++

        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")

        wrapper.innerHTML += `<span>(vraag ${taskIndex})</span><div class="grid"></div>`

        const content = wrapper.querySelector(".grid")

        let counter = 0;
        let connectCounter = 0;
        let connectLetterCounter = 0;

        shuffle(taskField.options).forEach(option => {
            counter++

            if (counter % 2 === 0) {
                indicator =  ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][connectLetterCounter++]
            } else {
                indicator = ++connectCounter
            }

            content.innerHTML += `
                <div class="choice ${counter % 2 === 0? "even": "odd"}"${taskField.field_type !== "connect"? ` onclick="selectOption(${taskField.id}, ${option.id})" id="task-option-${option.id}"` : ` id="${taskField.id}-${indicator}" option-id="${option.id}"`}>
                    ${taskField.field_type === "connect"? counter % 2 === 0? indicator : '' : '<div class="indicator"></div>'}
                    <div class="content">${option.content? option.content : ''}</div>
                    ${taskField.field_type === "connect" && counter % 2 !== 0? indicator : ''}
                </div>
            `
        })

        if (taskField.field_type === "connect") {
            wrapper.appendChild(connectAswerComponent(connectCounter, taskField.id))
        }
    } else if (taskField.field_type === "order") {
        taskIndex++

        wrapper.innerHTML = `<span>(vraag ${taskIndex})</span>`

        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")

        shuffle(taskField.options).forEach(option => {
            wrapper.innerHTML += `
                <div class="option" id="task-option-${option.id}" draggable="true" ondragstart="handleDragStart(event)" ondragover="handleDragOver(event)" ondrop="handleDrop(event)" task-id="${taskField.id}">
                    <div>${option.content? option.content : ''}</div>
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

    if (taskField.field_type === "header") {
        wrapper.innerHTML = `
            <h2><input onchange="editField(${taskField.id}, this.value)" value="${taskField.content? taskField.content : ""}" placeholder="Header"/></h2>
        `;
    } else if (taskField.field_type === "text") {
        wrapper.innerHTML = `
            <textarea onchange="editField(${taskField.id}, this.value)" placeholder="Text">${taskField.content? taskField.content : ""}</textarea>
        `;
    } else if (taskField.field_type === "image") {
        wrapper.appendChild(imageComponent(taskField.content? `${taskField.content}?psk=${getCookie("psk")}` : "/static/images/assets/notfound.webp"))
    } else if (taskField.field_type === "multiplechoice" || taskField.field_type === "checkboxes" || taskField.field_type === "connect") {
        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")

        wrapper.innerHTML += `<div class="grid"></div>`

        const content = wrapper.querySelector(".grid")

        let counter = 0;
        let connectCounter = 0;
        let connectLetterCounter = 0;

        taskField.options.forEach(option => {
            counter++

            if (counter % 2 === 0) {
                indicator =  ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][connectLetterCounter++]
            } else {
                indicator = ++connectCounter
            }

            content.innerHTML += `
                <div class="choice"${taskField.field_type !== "connect"? ` onclick="selectOption(${taskField.id}, ${option.id})" id="task-option-${option.id}"` : ` id="${taskField.id}-${indicator}" option-id="${option.id}"`}>
                    ${taskField.field_type === "connect"? counter % 2 === 0? indicator : '' : '<div class="indicator"></div>'}
                    <div class="content"><input type="text" onchange="editOption(${option.id}, this.value)" value="${option.content? option.content : ''}" placeholder="Option"/></div>
                    ${taskField.field_type === "connect" && counter % 2 !== 0? indicator : ''}
                </div>
            `
        })

        wrapper.innerHTML += `
            <button class="add-option" onclick="addOption(${taskField.id})">Add option</button>
        `

        if (taskField.field_type === "connect") {
            wrapper.appendChild(connectAswerComponent(connectCounter, taskField.id))
        }
    } else if (taskField.field_type === "order") {
        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")

        taskField.options.forEach(option => {
            wrapper.innerHTML += `
                <div class="option" id="task-option-${option.id}" draggable="true" ondragstart="handleDragStart(event)" ondragover="handleDragOver(event)" ondrop="handleDrop(event)" task-id="${taskField.id}">
                    <input type="text" onchange="editOption(${option.id}, this.value)" value="${option.content? option.content : ''}" placeholder="Option"/>
                </div>
            `
        })

        wrapper.innerHTML += `
            <button class="add-option" onclick="addOption(${taskField.id})">Add option</button>
        `
    }

    return wrapper;
}

function imageComponent(imageUrl) {
    const wrapper = document.createElement('img');

    wrapper.src = imageUrl;
    //wrapper.style.display = 'none';

    //wrapper.addEventListener('load', function() {
    //    console.log(wrapper, "event fired");

    //    wrapper.style.display = 'block';
    //});
   
    return wrapper
}

function connectAswerComponent(connectCounter, fieldId) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("connect-answer");

    for (let i = 0; i < connectCounter; i++) {
        const letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][i];

        wrapper.innerHTML += `
            <div class="column">
                <div class="row">${i + 1}</div>
                <div class="row"><input type="text" class="connect-answer" oninput="connectAnswer(${fieldId}, this)" placeholder="${letter}" index="${i + 1}"/></div>
            </div>
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