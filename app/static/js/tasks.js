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

    option.classList.toggle("active", !isSelected);
}