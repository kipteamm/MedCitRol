function professionComponent(profession) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("profession")
    wrapper.innerHTML = `
        <img src="/static/images/professions/${profession.toLowerCase()}.webp">

        <h2>${profession}</h2>
    `

    wrapper.onclick = function() {
        updateProfession(profession.toLowerCase())
    }

    return wrapper
}