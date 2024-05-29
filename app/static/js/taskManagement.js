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

    return window.location.href=`/teacher/task/${json.id}/edit${worldId? `?world=${worldId}` : ''}`;
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

    document.getElementById(`task-${taskId}`)?.remove();

    return;
}
