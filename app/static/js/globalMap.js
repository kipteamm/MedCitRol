const globalMap = document.getElementById('global-map');

function toggleMap(forceRemove=false) {
    cancelBuild();
    closeWorkPopup();

    if (forceRemove) {
        globalMap.classList.remove('active');

        return;
    }

    globalMap.classList.toggle('active');
}

function showSettlement(event, settlementId) {
    const settlement = document.getElementById(`id-${settlementId}`);

    settlement.classList.add("active");
}

function hideSettlement(settlementId) {
    const settlement = document.getElementById(`id-${settlementId}`);

    settlement.classList.remove("active");
}
