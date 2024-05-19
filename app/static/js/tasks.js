let answers = [];

function handleDragStart(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
}

function handleDragOver(event) {
    event.preventDefault();
}

function handleDrop(event, update) {
    event.preventDefault();

    const draggedId = event.dataTransfer.getData("text/plain");
    const draggedElement = document.getElementById(draggedId);
    const dropTarget = event.target.closest('.option');

    if (draggedElement && dropTarget) {
        const optionsContainer = document.getElementById(draggedElement.getAttribute("task-id"));
        const draggedIndex = Array.from(optionsContainer.children).indexOf(draggedElement);
        const dropIndex = Array.from(optionsContainer.children).indexOf(dropTarget);

        if (draggedIndex !== -1 && dropIndex !== -1) {
            if (draggedIndex < dropIndex) {
                optionsContainer.insertBefore(draggedElement, dropTarget.nextSibling);
            } else {
                optionsContainer.insertBefore(draggedElement, dropTarget);
            }
        }
    }

    const task = draggedElement.parentElement;
    let content = [];

    task.querySelectorAll(".option").forEach(option => {
        content.push(option.id.slice(3));
    })

    let answer = answers.find(field => field.field_id === task.id);

    if (answer) {
        answer.content = content;
    } else {
        answer = { field_id: task.id.slice(3), content: content };
        answers.push(answer);
    }

    if (update) return updateAnswer(draggedElement.parentElement.id.slice(3), content);
}

function selectOption(fieldId, optionId, update=false) {
    const option = document.getElementById(`id-${optionId}`);

    let answer = answers.find(field => field.field_id === fieldId);

    if (!answer) {
        answer = { field_id: fieldId, content: [] };
        answers.push(answer);
    }

    const isMultipleChoice = activeTaskJson.fields.some(field => field.field_type === "multiplechoice" && field.id === fieldId);
    const isSelected = answer.content.includes(optionId);

    if (isMultipleChoice && answer.content.length > 0) {
        const previousOptionId = answer.content[0];

        if (previousOptionId === optionId) return;

        answer.content = [optionId];

        const previousOption = document.getElementById(`id-${previousOptionId}`)
        
        if (previousOption) {
            previousOption.classList.remove("active"); 
        }
    } else if (isSelected) {
        answer.content.splice(answer.content.indexOf(optionId), 1);
    } else {
        answer.content.push(optionId);
    }

    if (!option) return;

    option.classList.toggle("active", !isSelected);

    if (update) return updateAnswer(fieldId, optionId);
}

function connectAnswer(fieldId, _input=null, update=false) {
    if (_input) {
        if (/[^a-zA-Z]/.test(_input.value)) return _input.value = '';
        if (_input.value.length > 1) return _input.value = _input.value[0];
    }

    let answer = answers.find(field => field.field_id === fieldId);

    if (!answer) {
        answer = { field_id: fieldId, content: [] };
        answers.push(answer);
    }

    answer.content = []

    document.getElementById(`id-${fieldId}`).querySelectorAll("input.connect-answer").forEach(input => {
        if (input.value) {
            const letter = input.value.toUpperCase()
            const indexOption = document.getElementById(`id-${fieldId}-${input.getAttribute("index")}`);
            const letterOption = document.getElementById(`id-${fieldId}-${letter}`)

            if (indexOption === null || letterOption === null) {
                input.value = "";

                sendAlert("error", "invalid option"); 

                return 
            } 

            if (answer.content.length > 0) {
                answer.content.forEach(_answer => {
                    if (_answer.split("%").includes(indexOption.getAttribute("option-id").slice(3)) || _answer.split("%").includes(letterOption.getAttribute("option-id").slice(3))) {
                        input.value = "";
                    } else {
                        const answerValue = `${indexOption.getAttribute("option-id").slice(3)}%${letterOption.getAttribute("option-id").slice(3)}`;

                        if (!answer.content.includes(answerValue)) {
                            answer.content.push(answerValue);

                            if (update) {
                                updateAnswer(fieldId, answerValue);
                            }
                        }
                    }
                });
            } else {
                const answerValue = `${indexOption.getAttribute("option-id").slice(3)}%${letterOption.getAttribute("option-id").slice(3)}`;

                answer.content.push(answerValue);

                if (update) {
                    updateAnswer(fieldId, answerValue);
                }
            }
        }
    });
}

async function submitTaskPreview(taskId) {
    const response = await fetch('/api/task/submit/preview', {
        method: "POST",
        body: JSON.stringify({task_id: taskId, answers: answers}),
        headers: {
            "Content-Type" : "application/json",
            "Authorization" : getCookie("psk")
        }
    });

    const json = await response.json();

    if (!response.ok) {
        alert(json.error);

        return;
    }

    alert(json.status);
}