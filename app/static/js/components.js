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
        wrapper.appendChild(taskFieldComponent(field));
    })

    return wrapper;
}

function taskFieldComponent(taskField) {
    const wrapper = document.createElement("div");

    wrapper.id = `id-${taskField.id}`;
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
        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")
        wrapper.innerHTML += `<div class="grid"></div>`

        const content = wrapper.querySelector(".grid")

        let counter = 0;
        let connectCounter = 0;
        let connectLetterCounter = 0;

        if (taskField.field_type === "connect") {
            options = orderedShuffle(taskField.options);
        } else {
            options = shuffle(taskField.options);
        }

        options.forEach(option => {
            counter++

            if (counter % 2 === 0) {
                indicator =  ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][connectLetterCounter++]
            } else {
                indicator = ++connectCounter
            }

            content.innerHTML += `
                <div class="choice ${counter % 2 === 0? "even": "odd"}"${taskField.field_type !== "connect"? ` onclick="selectOption('${taskField.id}', '${option.id}', false)" id="id-${option.id}"` : ` id="id-${taskField.id}-${indicator}" option-id="id-${option.id}"`}>
                    ${taskField.field_type === "connect"? counter % 2 === 0? indicator : '' : '<div class="indicator"></div>'}
                    <div class="content">${option.content? option.content : ''}</div>
                    ${taskField.field_type === "connect" && counter % 2 !== 0? indicator : ''}
                </div>
            `
        })

        if (taskField.field_type === "connect") {
            wrapper.appendChild(connectAswerComponent(taskField.options, taskField.id, false))
        }
    } else if (taskField.field_type === "order") {
        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")

        shuffle(taskField.options).forEach(option => {
            wrapper.innerHTML += `
                <div class="option" id="id-${option.id}" draggable="true" ondragstart="handleDragStart(event)" ondragover="handleDragOver(event)" ondrop="handleDrop(event, false)" task-id="id-${taskField.id}">
                    <div>${option.content? option.content : ''}</div>
                </div>
            `
        })
    }

    return wrapper;
}

let correctConnectAnswers = {};

function editableTaskFieldComponent(taskField) {
    const wrapper = document.createElement("div");

    wrapper.id = `id-${taskField.id}`;
    wrapper.classList.add("task-field");
    wrapper.setAttribute("onmouseover", "showActions(this)")
    wrapper.setAttribute("field-index", taskField.field_index)

    if (taskField.field_type === "header") {
        wrapper.innerHTML = `
            <h2><input onchange="editField('${taskField.id}', this.value)" value="${taskField.content? taskField.content : ""}" placeholder="Header"/></h2>
        `;
    } else if (taskField.field_type === "text") {
        wrapper.innerHTML = `
            <textarea onchange="editField('${taskField.id}', this.value)" placeholder="Text">${taskField.content? taskField.content : ""}</textarea>
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
            
                if (option.connected) {
                    correctConnectAnswers[option.connected] = indicator
                }
            } else {
                indicator = ++connectCounter

                correctConnectAnswers[`c-${indicator}`] = option.connected
            }

            content.innerHTML += `
                <div class="choice${option.answer? " active" : ""}"${taskField.field_type !== "connect"? ` id="id-${option.id}"` : ` id="id-${taskField.id}-${indicator}" option-id="id-${option.id}"`}>
                    ${taskField.field_type === "connect"? counter % 2 === 0? indicator : '' : `<div class="indicator"${taskField.field_type !== "connect"? `onclick="selectOption('${taskField.id}', '${option.id}', true)"` : ''}></div>`}
                    <div class="content"><input type="text" onchange="editOption('${option.id}', this.value)" value="${option.content? option.content : ''}" placeholder="Option"/></div>
                    ${taskField.field_type === "connect" && counter % 2 !== 0? indicator : ''}
                </div>
            `

            if (option.answer) {
                selectOption(taskField.id, option.id, false)
            }
        })

        wrapper.innerHTML += `
            <button class="add-option" onclick="addOption('${taskField.id}')">Add option</button>
        `

        if (taskField.field_type === "connect") {
            wrapper.appendChild(connectAswerComponent(taskField.options, taskField.id, true))
        }
    } else if (taskField.field_type === "order") {
        wrapper.classList.add(taskField.field_type)
        wrapper.classList.add("question")

        const map = new Map(taskField.options.map(item => [item.id, item]));
        const sorted = [];

        let currentItem = taskField.options.find(item => item.connected === null);

        while (currentItem) {
            sorted.push(currentItem);
            currentItem = map.get(currentItem.id);

            if (currentItem) {
                currentItem = taskField.options.find(item => item.connected === currentItem.id);
            }
        }

        sorted.forEach(option => {
            const previous = wrapper.querySelector(`#id-${option.connected}`);

            if (previous) {
                previous.insertAdjacentElement("afterend", orderOption(option, taskField.id));
            } else {
                wrapper.prepend(orderOption(option, taskField.id));
            }
        })

        wrapper.innerHTML += `
            <button class="add-option" onclick="addOption('${taskField.id}')">Add option</button>
        `
    }

    return wrapper;
}

function orderOption(option, taskFieldId) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("option");
    wrapper.id = `id-${option.id}`;
    wrapper.draggable = true;
    wrapper.setAttribute("ondragstart", "handleDragStart(event)");
    wrapper.setAttribute("ondragover", "handleDragOver(event)");
    wrapper.setAttribute("ondrop", "handleDrop(event, true)");
    wrapper.setAttribute("task-id", `id-${taskFieldId}`);

    wrapper.innerHTML += `<input type="text" onchange="editOption('${option.id}', this.value)" value="${option.content? option.content : ''}" placeholder="Option"/>`;

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

function connectAswerComponent(options, fieldId, update) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("connect-answer");

    let columnIndex = 0;
    let content = [];
    let index = 0;

    options.forEach(option => {
        let column = wrapper.querySelector(`#column-${columnIndex}`);

        if (!column) {
            column = document.createElement("div");

            column.id = `column-${columnIndex}`
            column.classList.add("column");

            wrapper.appendChild(column);
        }

        const row = document.createElement("div");

        row.classList.add("row");

        if (index % 2 === 0) {
            row.innerHTML = columnIndex + 1
        } else {
            const letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][columnIndex];

            row.innerHTML = `<input type="text" class="connect-answer" oninput="connectAnswer('${fieldId}', this, ${update})" placeholder="${letter}" index="${columnIndex + 1}" ${option.connected? `value="${correctConnectAnswers[options.find(_option => _option.id === correctConnectAnswers[`c-${columnIndex + 1}`]).connected]}` : ''}"/>`;

            columnIndex++;

            if (option.connected) {
                content.push(`${option.connected}%${options.find(_option => _option.id === option.connected).connected}`)
            }
        }

        column.appendChild(row);

        index++;
    })

    if (content.length > 0) {
        answers.push({field_id : fieldId, content : content});
    }

    return wrapper;
}

function workStatusComponent(shouldBuild=false) {
    const wrapper = document.createElement("div");

    if (shouldBuild) {
        wrapper.innerHTML = `
            <h2>Unfinished buildings!</h2>
            <p>
                You have some unbuild things left over. Placing buildings can potentially improve your productivity. Check the build menu for more!
            </p>
            <button class="primary-btn" onclick="openBuildMenu(false)">Build menu</button>
            <button class="primary-btn" onclick="loadTask()">Work anyway</button>
            <button class="primary-btn" onclick="closeWorkPopup()">Close</button>
        `
    } else {
        let action = 'Milling';
        let reactant = 'rye';
        let product = 'flower';
        let recommendedAmount = 4;

        if (character.profession === 'baker') {
            action = 'Baking';
            reactant = 'rye_flour';
            product = 'bread';
            recommendedAmount = 16;
        }

        const item = character.inventory.find(item => item.item_type === reactant);

        let amount = 0;

        if (item) {
            amount = item.amount;
        }

        wrapper.innerHTML = `
            <h2>${action}</h2>
            <p>
                You are not getting everything out of your day! You can buy more ${reactant} to produce more ${product}. You have ${amount} out of the recommended ${recommendedAmount} ${reactant}.
            </p>
            <button class="primary-btn" onclick="openMarket()">Visit market</button>
            <button class="primary-btn" onclick="loadTask()">Work anyway</button>
            <button class="primary-btn" onclick="closeWorkPopup()">Close</button>
        `
    }

    return wrapper;
}

function inventoryItemComponent(item, building) {
    const wrapper = document.createElement("div");

    wrapper.id = `id-${item.id}`;
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

    wrapper.id = `id-${item.id}`;
    wrapper.classList.add("market-item");
    wrapper.innerHTML = `
        <h3>${item.item_type}</h3>
        <i>${item.seller}${item.character_id === character.id? " (you)" : ""}</i><br>
        <b><span id="amount-${item.id}">${amountComponent(item.amount)}</span></b><br>
        ${item.character_id !== character.id? `<button class="primary-btn" onclick="buyItem('${item.id}')">Buy <b>(${item.price} penningen/item)</b></button>` : `<b>${item.price} penningen/item</b>`}
    `;

    return wrapper;
}

function supplyComponent(item) {
    const wrapper = document.createElement("div");

    wrapper.innerHTML = `
        ${item.item_type} <b>${item.amount}x</b>
    `

    return wrapper;
}

function amountComponent(amount) {
    if (amount < 5) return "Very limited supply";
    if (amount < 10) return "Limited supply";
    if (amount < 15) return "Almost out of stock";
    if (amount < 20) return "Low on stock";
    if (amount < 25) return "Quite Stocked";
    if (amount < 30) return "Well stocked";
    if (amount < 35) return "Very stocked";
    
    return "Huge supply"
}


function informationComponent(tile) {
    const wrapper = document.createElement("div");

    let future = '';

    if (tile.character_id) {
        owner = tile.character_id === character.id? `<p>This is your ${tile.tile_type}</p>` : `<p>This is owned by ${tile.name} ${tile.surname}.</p>`;
    } else {
        owner = `<p>This is owned by ${character.id? "your" : "the"} ruler (${settlementRuler.name} ${settlementRuler.surname}).</p>`;

        if (tile.tile_type === "claimed") {
            future = `<p>This will become a ${tile.future}</p>`;
        }
    }

    if (tile.tile_type === "warehouse") {
        loadWarehouse(tile.id);
    }

    wrapper.innerHTML = `
        <h2>${tile.tile_type}</h2>
        ${owner}
        ${future}
        <div id="warehouse-items"></div>
    `

    return wrapper;
}