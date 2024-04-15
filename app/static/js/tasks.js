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