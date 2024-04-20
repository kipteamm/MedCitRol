let answers = [];

function handleDragStart(event) {
    event.dataTransfer.setData("text/plain", event.target.id);
}

function handleDragOver(event) {
    event.preventDefault();
}

function handleDrop(event) {
    event.preventDefault();

    const draggedId = event.dataTransfer.getData("text/plain");
    const draggedElement = document.getElementById(draggedId);
    const dropTarget = event.target.closest('.option');

    if (draggedElement && dropTarget) {
        const optionsContainer = document.getElementById(`task-field-${draggedElement.getAttribute("task-id")}`);
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
        content.push(parseInt(option.id.split("-")[2]));
    })

    let answer = answers.find(field => field.field_id === task.id.split("-")[2]);

    if (answer) {
        answer.content = content;
    } else {
        answer = { field_id: parseInt(task.id.split("-")[2]), content: content };
        answers.push(answer);
    }
}

function selectOption(fieldId, optionId) {
    const option = document.getElementById(`task-option-${optionId}`);

    let answer = answers.find(field => field.field_id === fieldId);

    if (!answer) {
        answer = { field_id: fieldId, content: [] };
        answers.push(answer);
    }

    const isMultipleChoice = activeTaskJson.fields.some(field => field.field_type === "multiplechoice" && field.id === fieldId);
    const isSelected = answer.content.includes(optionId);

    if (isMultipleChoice && answer.content.length > 0) {
        const previousOptionId = answer.content[0];
        document.getElementById(`task-option-${previousOptionId}`).classList.remove("active"); 
        answer.content = [optionId];
    } else if (isSelected) {
        answer.content.splice(answer.content.indexOf(optionId), 1);
    } else {
        answer.content.push(optionId);
    }

    if (!option) return;

    option.classList.toggle("active", !isSelected);
}

function connectAnswer(fieldId, _input=null) {
    if (input) {
        if (/[^a-zA-Z]/.test(_input.value)) return _input.value = '';
        if (_input.value.length > 1) return _input.value = _input.value[0];
    }

    let answer = answers.find(field => field.field_id === fieldId);

    if (!answer) {
        answer = { field_id: fieldId, content: [] };
        answers.push(answer);
    }

    answer.content = []

    document.getElementById(`task-field-${fieldId}`).querySelectorAll("input.connect-answer").forEach(input => {
        if (input.value) {
            const letter = input.value.toUpperCase()
            const indexOption = document.getElementById(`${fieldId}-${input.getAttribute("index")}`);
            const letterOption = document.getElementById(`${fieldId}-${letter}`)

            if (indexOption === null || letterOption === null) {
                input.value = "";

                sendAlert("error", "invalid option"); 

                return 
            } 

            if (answer.content.length > 0) {
                answer.content.forEach(_answer => {
                    if (_answer.split("-").includes(indexOption.getAttribute("option-id")) || _answer.split("-").includes(letterOption.getAttribute("option-id"))) {
                        input.value = "";
                    } else {
                        const answerValue = `${indexOption.getAttribute("option-id")}-${letterOption.getAttribute("option-id")}`;

                        if (!answer.content.includes(answerValue)) {
                            answer.content.push(answerValue);
                        }
                    }
                });
            } else {
                answer.content.push(`${indexOption.getAttribute("option-id")}-${letterOption.getAttribute("option-id")}`);
            }
        }
    });
}