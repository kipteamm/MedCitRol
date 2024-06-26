async function duplicateTask(taskId, worldId) {
    const response = await fetch(`/api/task/duplicate`, {
        method: "POST",
        body: JSON.stringify({task_id : taskId, world_id : worldId}),
        headers: {
            'Authorization': `${getCookie('token')}`,
            'Content-Type': 'application/json',
        },
    })

    const json = await response.json();

    if (!response.ok) {
        return console.log(response, json);
    }

    return window.location.href=`/task/${json.id}/edit${worldId? `?world=${worldId}` : ''}`;
}

async function deleteTask(taskId, worldId) {
    let world = '';
    
    if (worldId) {
        world = `?world=${worldId}`
    }

    const response = await fetch(`/api/task/${taskId}/delete${world}`, {
        method: "DELETE",
        headers: {
            'Authorization': `${getCookie('token')}`,
        },
    })

    if (!response.ok) {
        return console.log(response, await response.json());
    }

    if (!worldId) return document.getElementById(`task-${taskId}`)?.remove();
    
    const worldTask = document.getElementById(`task-${taskId}-${worldId}`);

    worldTask.parentElement.querySelectorAll('div.world-task').length === 1? worldTask.parentElement.remove() : worldTask.remove();

    return;
}
