function taskUserElementComponent(userId) {
    const wrapper = document.createElement("div");

    wrapper.classList.add("task-user")
    wrapper.id = userId;

    return wrapper;
}

function taskUserEntryComponent(taskUser, first) {
    const wrapper = document.createElement("div");

    wrapper.classList.add(first? 'first' : 'other')
    wrapper.innerHTML = `${taskUser.email} - ${taskUser.percentage}%${first? `&emsp;&emsp;<a onclick="toggleMore('${taskUser.user_id}')">Previous attempts</a>`: ''}`

    return wrapper;
}

function loadUsers() {
    taskInfo.forEach(taskUser => {
        let taskUserElement = document.getElementById(taskUser.user_id);
        let first = false;

        if (!taskUserElement) {
            taskUserElement = taskUserElementComponent(taskUser.user_id);

            taskUsers.appendChild(taskUserElement);
            first = true;
        }

        taskUserElement.appendChild(taskUserEntryComponent(taskUser, first))
    })
}

function toggleMore(userId) {
    document.getElementById(userId).classList.toggle('active');
}