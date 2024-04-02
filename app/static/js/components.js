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

    console.log(task)

    wrapper.classList.add("task");
    wrapper.innerHTML = `
        task
        ${task}
    `;

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
        wrapper.onclick = function() {selectItem(item.id)}
    }

    return wrapper
}